# domain/prakriti/service.py
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
from .models import GeneratePrakritiRequest, GeneratePrakritiResponse
from .validators import ensure_questions_reasonable


SYSTEM_PROMPT = (
    "You are an Ayurvedic practitioner. Assess prakriti (constitutional balance) "
    "based on profile and answers. Provide concise, evidence-consistent guidance. "
    "Output ONLY valid JSON matching the schema."
)

class PrakritiService:
    def __init__(self, llm: LLMClient, cache: Cache | None):
        self.llm = llm
        self.cache = cache

    def _ck(self, payload: dict) -> str:
        blob = json.dumps(payload, sort_keys=True).encode()
        return f"prakriti:{hashlib.sha256(blob).hexdigest()}"

    async def generate(self, req: GeneratePrakritiRequest) -> Tuple[GeneratePrakritiResponse, Dict[str, Any]]:
        ensure_questions_reasonable(len(req.questions))
        pv = req.prompt_version or int(features().get("prompt_versions", {}).get("prakriti", 1))

        context = {
            "profile": req.profile.model_dump(),
            "questions": [q.model_dump() for q in req.questions],
        }
        user_prompt = render_prompt("prakriti", pv, context)
        schema_name, schema = schema_by_task("prakriti")

        ck = self._ck({"p": req.profile.model_dump(), "qs": [q.model_dump() for q in req.questions], "pv": pv, "mo": req.model})
        if self.cache and not req.force:
            cached = await self.cache.get(ck)
            if cached:
                try:
                    return GeneratePrakritiResponse.model_validate(cached["data"]), {**cached["meta"], "cached": True}
                except ValidationError:
                    pass

        resp = await self.llm.structured(
            task="prakriti",
            system=SYSTEM_PROMPT,
            user=user_prompt,
            schema_name=schema_name,
            schema=schema,
            model_override=req.model,
        )

        try:
            data = GeneratePrakritiResponse.model_validate({
                **resp.data,
                "meta": {"model": resp.model, "prompt_version": pv, "cached": False},
            })
        except ValidationError as ve:
            raise ValueError(f"Invalid prakriti assessment schema: {ve}")

        if self.cache:
            await self.cache.setex(ck, None, {"data": data.model_dump(), "meta": data.meta})

        return data, data.meta
