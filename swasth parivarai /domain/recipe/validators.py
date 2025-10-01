# domain/recipe/validators.py
from __future__ import annotations
from pydantic import BaseModel, ValidationError

def ensure_non_empty(value: str, field_name: str = "value") -> None:
    if not value or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
