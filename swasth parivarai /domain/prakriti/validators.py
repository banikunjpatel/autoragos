# domain/prakriti/validators.py
from __future__ import annotations

def ensure_questions_reasonable(count: int, max_allowed: int = 50) -> None:
    if count < 0 or count > max_allowed:
        raise ValueError(f"Number of questions must be between 0 and {max_allowed}")
