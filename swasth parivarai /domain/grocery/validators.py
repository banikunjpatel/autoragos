# domain/grocery/validators.py
from __future__ import annotations

def ensure_household(size: int) -> tuple[str, int]:
    return ("single" if size <= 1 else "family", max(1, size))
