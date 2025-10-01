# llm/tasks.py
from __future__ import annotations

"""
Task keys used across the LLM layer and config/model_map.yml.

Keep these stable; they are referenced by:
- config/model_map.yml
- schemas/* (via llm/schema_registry.py defaults)
- prompts/<task>/vN.j2
"""

# Canonical task names (lower_snake)
MEAL_PLAN = "meal_plan"
RECIPE = "recipe"
GROCERY = "grocery"
PRAKRITI = "prakriti"

# Useful collections
ALL_TASKS: tuple[str, ...] = (MEAL_PLAN, RECIPE, GROCERY, PRAKRITI)


def normalize_task(task: str) -> str:
    """
    Normalize incoming task labels to the canonical keys above.
    Accepts a few common aliases.
    """
    t = (task or "").strip().lower().replace(" ", "_")

    if t in {"meal", "mealplan", "meal_plan"}:
        return MEAL_PLAN
    if t in {"rec", "recipes", "recipe"}:
        return RECIPE
    if t in {"groceries", "grocery_list", "grocery"}:
        return GROCERY
    if t in {"prakruti", "prakriti", "dosha_assessment", "prakriti_assessment"}:
        return PRAKRITI

    # Fallback: return as-is (caller may still handle via config)
    return t
