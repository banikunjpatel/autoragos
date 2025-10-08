# app/lifespan.py
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

import os
from db.mongo import init_mongo, close_mongo
from db.rotation_repo import RotationRepository

from fastapi import FastAPI

from config import (
    features,
    feature_flag,
    llm_defaults,
    model_map,
    env as env_settings,
)
from cache import init_cache, close_cache
from llm.client import LLMClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    App startup/shutdown.
    - Initializes shared LLM client (task→model aware)
    - Initializes cache (optional, per features.yml)
    - Exposes config snapshots on app.state for easy access
    """
    # ---- Resolve runtime config
    feat = features()
    timeout_s = int(llm_defaults()["request_timeout_s"])
    use_cache = bool(feature_flag("enable_caching", True))
    cache_ttl = int(feature_flag("cache_ttl_seconds", 604800))
    task_models = model_map()

    # ---- Init resources
    cache = await init_cache(enabled=use_cache, default_ttl_seconds=cache_ttl)
    llm = LLMClient(
        api_key=env_settings.OPENAI_API_KEY,
        request_timeout_s=timeout_s,
        task_model_map=task_models,
    )
    
    db = await init_mongo(os.getenv("MONGO_URL"), os.getenv("MONGO_DB"))
    rotation_repo = RotationRepository(db) if db else None

    app.state.db = db
    app.state.rotation_repo = rotation_repo

    # ---- Expose on app.state
    app.state.features = feat
    app.state.model_map = task_models
    app.state.cache = cache
    app.state.llm = llm

    try:
        yield
    finally:
        # ---- Graceful shutdown
        await close_cache(cache)
        await close_mongo()
        await llm.aclose()