# domain/grocery/service.py
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Tuple

from pydantic import ValidationError

from config import features
from cache import Cache
from llm.client import LLMClient
from llm.prompt_renderer import render_prompt
from llm.schema_registry import schema_by_task
from domain.meal.models import WeeklyMealPlan
from domain.meal.grocery_aggregators import aggregate_from_plan
from .models import GenerateGroceryListRequest, GenerateGroceryListResponse, GroceryItem, Household


SYSTEM_PROMPT = (
    "You are an organized Indian grocery planner. Aggregate a weekly grocery list with metric units. "
    "Use Indian market categories. Output ONLY valid JSON matching the schema."
)

class GroceryService:
    def __init__(self, llm: LLMClient, cache: Cache | None):
        self.llm = llm
        self.cache = cache

    def _ck(self, payload: dict) -> str:
        blob = json.dumps(payload, sort_keys=True).encode()
        return f"grocery:{hashlib.sha256(blob).hexdigest()}"

    async def from_meal_plan(self, plan: WeeklyMealPlan) -> list[GroceryItem]:
        return aggregate_from_plan(plan)

    async def generate(self, req: GenerateGroceryListRequest) -> Tuple[GenerateGroceryListResponse, Dict[str, Any]]:
        # Option A: derive server-side from meal plan if provided
        if req.mealPlan:
            plan = WeeklyMealPlan.model_validate(req.mealPlan)
            items = await self.from_meal_plan(plan)
            data = GenerateGroceryListResponse(
                region=plan.region,
                dietType=plan.dietType,
                household=Household(type=plan.household.type, size=plan.household.size),
                items=items,
                notes=None,
                meta={"source": "server_aggregator", "cached": False},
            )
            return data, data.meta

        # Option B: LLM-based generation
        pv = req.prompt_version or int(features().get("prompt_versions", {}).get("grocery", 1))
        context = {
            "region": req.region,
            "diet_type": req.dietType,
            "household": req.household.model_dump(),
        }
        user_prompt = render_prompt("grocery", pv, context)
        schema_name, schema = schema_by_task("grocery")

        ck = self._ck({"r": req.region, "d": req.dietType, "h": req.household.model_dump(), "pv": pv, "mo": req.model})
        if self.cache and not req.force:
            cached = await self.cache.get(ck)
            if cached:
                try:
                    return GenerateGroceryListResponse.model_validate(cached["data"]), {**cached["meta"], "cached": True}
                except ValidationError:
                    pass

        resp = await self.llm.structured(
            task="grocery",
            system=SYSTEM_PROMPT,
            user=user_prompt,
            schema_name=schema_name,
            schema=schema,
            model_override=req.model,
        )

        try:
            data = GenerateGroceryListResponse.model_validate({
                **resp.data,
                "meta": {"model": resp.model, "prompt_version": pv, "cached": False},
            })
        except ValidationError as ve:
            raise ValueError(f"Invalid grocery list schema: {ve}")

        if self.cache:
            await self.cache.setex(ck, None, {"data": data.model_dump(), "meta": data.meta})

        return data, data.meta
