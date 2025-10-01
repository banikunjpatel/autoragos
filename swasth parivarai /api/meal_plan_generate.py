# api/v1/meal/meal_plan_generate.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from config import features
from domain.meal.models import GenerateMealPlanRequest, GenerateMealPlanResponse
from domain.meal.service import MealPlanService

from deps import model_override, prompt_version_override

router = APIRouter(tags=["meal"])


@router.post("/meal-plan/generate", response_model=GenerateMealPlanResponse)
async def generate_meal_plan(
    request: Request,
    body: GenerateMealPlanRequest,
    x_model: str | None = Depends(model_override),
    x_prompt_ver: int | None = Depends(prompt_version_override),
):
    # Merge header overrides if allowed
    feats = features()
    allow_override = bool(feats.get("allow_model_override", True))
    model = x_model if (allow_override and x_model) else body.model
    prompt_version = x_prompt_ver if x_prompt_ver is not None else body.prompt_version

    # Resolve service dependencies from app.state
    llm = request.app.state.llm
    cache = request.app.state.cache

    svc = MealPlanService(llm=llm, cache=cache)
    final_req = body.model_copy(update={"model": model, "prompt_version": prompt_version})

    plan, meta = await svc.generate(final_req)
    return GenerateMealPlanResponse(plan=plan, meta=meta)
