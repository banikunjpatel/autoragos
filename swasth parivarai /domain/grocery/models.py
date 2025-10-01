# domain/grocery/models.py
from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

DietType = Literal["veg", "non_veg", "eggs_ok"]

class Household(BaseModel):
    type: Literal["single", "family"]
    size: int = Field(ge=1)

class GroceryItem(BaseModel):
    name: str
    qty: float
    unit: str
    category: Optional[str] = None

class GenerateGroceryListRequest(BaseModel):
    region: str
    dietType: DietType
    household: Household
    # Option A: derive from a meal plan payload (recommended)
    mealPlan: Optional[dict] = None
    # Option B: use LLM to generate de novo
    use_llm: bool = False
    model: Optional[str] = None
    prompt_version: Optional[int] = None
    force: bool = False

class GenerateGroceryListResponse(BaseModel):
    region: str
    dietType: DietType
    household: Household
    items: List[GroceryItem]
    notes: Optional[str] = None
    meta: dict
