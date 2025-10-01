# api/v1/grocery/grocery_categories_get.py
from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["grocery"])
DATA_DIR = Path(__file__).resolve().parents[3] / "data"

@router.get("/grocery/categories")
async def grocery_categories() -> dict:
    path = DATA_DIR / "grocery_categories.json"
    if not path.exists():
        raise HTTPException(status_code=500, detail="categories data not found")
    return {"categories": path.read_text(encoding="utf-8")}
