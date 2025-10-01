# api/v1/deps.py
from __future__ import annotations

from typing import Optional

from fastapi import Header

from app.core.config import features


async def model_override(x_model: Optional[str] = Header(default=None)) -> Optional[str]:
    if not bool(features().get("allow_model_override", True)):
        return None
    return x_model


async def prompt_version_override(x_prompt_version: Optional[int] = Header(default=None)) -> Optional[int]:
    return x_prompt_version
