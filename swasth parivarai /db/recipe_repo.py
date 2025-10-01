# db/repositories/recipe_repo.py
from __future__ import annotations

from typing import Any, Optional

class RecipeRepository:
    def __init__(self, db: Optional[Any]):
        self.db = db
        self.col = db["recipes"] if db else None

    async def save(self, doc: dict) -> Optional[str]:
        if not self.col:
            return None
        res = await self.col.insert_one(doc)
        return str(res.inserted_id)

    async def get(self, _id: str) -> Optional[dict]:
        if not self.col:
            return None
        return await self.col.find_one({"_id": _id})
