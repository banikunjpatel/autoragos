# llm/model_router.py
from __future__ import annotations

from typing import Optional

from config import model_map, features, llm_defaults
from .tasks import normalize_task


class ModelRouter:
    """
    Chooses the OpenAI model for a given logical task.

    Precedence:
      1) explicit override (if allow_model_override is true)
      2) model_map.yml (or TASK_MODELS__* env overrides)
      3) llm defaults from settings.yml (quality/fast) as fallback
    """

    def __init__(self) -> None:
        self._models = model_map()
        self._features = features()
        self._defaults = llm_defaults()

    def refresh(self) -> None:
        """Re-read config (rarely needed; app restarts typically update caches)."""
        self._models = model_map()
        self._features = features()
        self._defaults = llm_defaults()

    def select(self, task: str, override: Optional[str] = None) -> str:
        t = normalize_task(task)
        # 1) header/body override (if enabled)
        if override and bool(self._features.get("allow_model_override", True)):
            return override

        # 2) model_map.yml (merged with env)
        if t in self._models:
            return self._models[t]

        # 3) sensible fallbacks
        # Default to the "quality" model for unknown tasks
        return self._defaults.get("quality_model", "gpt-4o")


# Convenience function (stateless usage)
def select_model(task: str, override: Optional[str] = None) -> str:
    return ModelRouter().select(task, override)
