# domain/meal/aggregators/grocery.py
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Tuple

from .models import GroceryItem, WeeklyMealPlan


def _key(name: str, unit: str) -> Tuple[str, str]:
    return (name.strip().lower(), unit.strip().lower())


def aggregate_from_plan(plan: WeeklyMealPlan) -> list[GroceryItem]:
    """
    Deterministically aggregate ingredients across all meals in the plan.
    Group by (name, unit); sum qty; keep first non-empty category.
    """
    sums: Dict[Tuple[str, str], float] = defaultdict(float)
    cats: Dict[Tuple[str, str], str] = {}

    for day in plan.days:
        for meal in (day.breakfast, day.lunch, day.dinner):
            for ing in meal.recipe.ingredients:
                k = _key(ing.name, ing.unit)
                sums[k] += float(ing.qty)
                if k not in cats and ing.category:
                    cats[k] = ing.category

    items: list[GroceryItem] = []
    for (name, unit), qty in sums.items():
        items.append(
            GroceryItem(name=name, qty=round(qty, 4), unit=unit, category=cats.get((name, unit)))
        )
    # Optional: sort for stable output
    items.sort(key=lambda g: (g.category or "zz", g.name))
    return items
