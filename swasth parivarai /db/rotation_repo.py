# db/repositories/rotation_repo.py
from __future__ import annotations
from typing import Any, Optional, List
from datetime import datetime, timedelta

class RotationRepository:
    """
    Tracks dishes used per user per week to avoid repeats across weeks.
    Schema: { userId, weekStart: 'YYYY-MM-DD', dishes: [str], createdAt }
    """

    def __init__(self, db: Optional[Any]):
        self.db = db
        self.col = db["dish_rotation"] if db else None

    async def record_week(self, user_id: str, week_start: str, dishes: List[str]) -> None:
        if not self.col:
            return
        await self.col.update_one(
            {"userId": user_id, "weekStart": week_start},
            {"$set": {"dishes": dishes, "createdAt": datetime.utcnow()}},
            upsert=True,
        )

    async def recent_dishes(self, user_id: str, weeks: int) -> set[str]:
        if not self.col or weeks <= 0:
            return set()
        # fetch last N weeks — simplest: just fetch many and filter in app
        cursor = self.col.find({"userId": user_id}).sort("weekStart", -1).limit(12)
        recent: set[str] = set()
        async for doc in cursor:
            for d in (doc.get("dishes") or []):
                recent.add(str(d).strip().lower())
            if len(recent) > 2000:  # cap to avoid memory blowups
                break
        return recent
