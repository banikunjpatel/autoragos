# domain/recipe/models.py
from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

DietType = Literal["veg", "non_veg", "eggs_ok"]

class Ingredient(BaseModel):
    name: str
    qty: float = Field(ge=0)
    unit: str
    category: Optional[str] = None

class RecipeDetail(BaseModel):
    ingredients: List[Ingredient]
    steps: List[str]
    prep_mins: int = Field(ge=0)
    cook_mins: int = Field(ge=0)

class GenerateRecipeRequest(BaseModel):
    dish: str
    region: str
    dietType: DietType
    servings: int = Field(ge=1)
    model: Optional[str] = None
    prompt_version: Optional[int] = None
    force: bool = False

class GenerateRecipeResponse(BaseModel):
    dish: str
    region: str
    dietType: DietType
    servings: int
    recipe: RecipeDetail
    notes: Optional[str] = None
    meta: dict
