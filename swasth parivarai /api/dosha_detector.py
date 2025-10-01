# api/v1/prakriti/prakriti_assessment.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from config import features
from domain.prakriti.models import GeneratePrakritiRequest, GeneratePrakritiResponse
from domain.prakriti.service import PrakritiService
from deps import model_override, prompt_version_override

router = APIRouter(tags=["prakriti"])

@router.post("/prakriti/assessment", response_model=GeneratePrakritiResponse)
async def prakriti_assessment(
    request: Request,
    body: GeneratePrakritiRequest,
    x_model: str | None = Depends(model_override),
    x_prompt_ver: int | None = Depends(prompt_version_override),
):
    feats = features()
    allow_override = bool(feats.get("allow_model_override", True))
    model = x_model if (allow_override and x_model) else body.model
    prompt_version = x_prompt_ver if x_prompt_ver is not None else body.prompt_version

    svc = PrakritiService(llm=request.app.state.llm, cache=request.app.state.cache)
    final_req = body.model_copy(update={"model": model, "prompt_version": prompt_version})

    data, meta = await svc.generate(final_req)
    return data
