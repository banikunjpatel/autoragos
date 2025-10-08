# domain/meal/variety.py
from __future__ import annotations
from typing import List, Tuple
from .models import WeeklyMealPlan

def collect_dish_names(plan: WeeklyMealPlan) -> List[str]:
    names = []
    for day in plan.days:
        names.extend([day.breakfast.name, day.lunch.name, day.dinner.name])
    return names

def find_duplicates(names: List[str]) -> List[str]:
    seen, dups = set(), set()
    for n in names:
        key = n.strip().lower()
        if key in seen:
            dups.add(key)
        else:
            seen.add(key)
    return sorted(list(dups))

def filter_recent(names: List[str], recent: set[str]) -> List[str]:
    bad = []
    for n in names:
        if n.strip().lower() in recent:
            bad.append(n)
    return bad