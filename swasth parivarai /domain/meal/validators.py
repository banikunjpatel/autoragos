# domain/meal/validators.py
from __future__ import annotations

from datetime import date
from typing import Iterable

from .models import FamilyMember


def infer_household(members: Iterable[FamilyMember]) -> tuple[str, int]:
    ml = list(members)
    size = len(ml)
    return ("single" if size <= 1 else "family", max(1, size))


def validate_week_start(week_start: str) -> None:
    try:
        date.fromisoformat(week_start)
    except Exception as e:
        raise ValueError("weekStart must be an ISO date (YYYY-MM-DD)") from e
