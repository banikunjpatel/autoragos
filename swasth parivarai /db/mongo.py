# db/mongo.py
from __future__ import annotations

from typing import Any, Optional

MONGO_AVAILABLE = False
try:
    import motor.motor_asyncio as motor  # type: ignore
    MONGO_AVAILABLE = True
except Exception:
    motor = None  # type: ignore

_client = None
_db = None

async def init_mongo(url: str | None, db_name: str | None = None) -> Optional[Any]:
    """
    Initialize Motor client if motor and URL are available.
    Returns the database handle or None if not configured.
    """
    global _client, _db
    if not (MONGO_AVAILABLE and url):
        return None
    _client = motor.AsyncIOMotorClient(url)  # type: ignore
    _db = _client.get_default_database() if not db_name else _client[db_name]
    return _db

async def get_db() -> Optional[Any]:
    return _db

async def close_mongo() -> None:
    global _client, _db
    if _client:
        _client.close()
    _client = None
    _db = None
