# domain/meal/models.py
from __future__ import annotations

from typing import List, Literal, Optional
from datetime import datetime
from typing import Dict
from pydantic import BaseModel, Field


Dosha = Literal["vata", "pitta", "kapha", "tridoshic"]
DietType = Literal["veg", "non_veg", "eggs_ok"]


class FamilyMember(BaseModel):
    name: str
    dosha: Dosha


class Ingredient(BaseModel):
    name: str
    qty: float = Field(ge=0)
    unit: str
    category: Optional[str] = None  # produce|grains|dairy|spices|protein|staples|bakery|condiments|other


class Recipe(BaseModel):
    ingredients: List[Ingredient]
    steps: List[str]
    prep_mins: int = Field(ge=0)
    cook_mins: int = Field(ge=0)


class Meal(BaseModel):
    name: str
    serving_size: int = Field(ge=1)
    recipe: Recipe


class DayPlan(BaseModel):
    date: str
    breakfast: Meal
    lunch: Meal
    dinner: Meal
    notes: Optional[str] = None


class Household(BaseModel):
    type: Literal["single", "family"]
    size: int = Field(ge=1)
    members: List[FamilyMember]


class GroceryItem(BaseModel):
    name: str
    qty: float
    unit: str
    category: Optional[str] = None


class WeeklyMealPlan(BaseModel):
    weekStart: str
    region: str
    dietType: DietType
    household: Household
    days: List[DayPlan] = Field(min_length=7, max_length=7)
    groceryList: List[GroceryItem]


# API DTOs
class GenerateMealPlanRequest(BaseModel):
    userId: str
    weekStart: str
    region: str
    dietType: DietType
    members: List[FamilyMember]
    model: Optional[str] = None
    prompt_version: Optional[int] = None
    force: bool = False


class GenerateMealPlanResponse(BaseModel):
    plan: WeeklyMealPlan
    meta: dict

class MealPlanDocument(BaseModel):
    userId: str
    plan: WeeklyMealPlan
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    wellnessTips: Optional[Dict[str, List[str]]] = Field(default_factory=dict)
    modelMeta: Optional[dict] = None