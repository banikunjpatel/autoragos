# llm/client.py
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from openai import AsyncOpenAI
from openai import APIError, APITimeoutError, RateLimitError


@dataclass
class StructuredResult:
    """Return type for structured JSON generations."""
    data: Dict[str, Any]
    model: str
    raw: Any  # raw SDK response object


class LLMClient:
    """
    Thin adapter over OpenAI Responses API.
    - Picks model per task from a provided task_model_map
    - Supports per-call model override
    - Provides a structured() helper that enforces a JSON schema
    """

    def __init__(
        self,
        *,
        api_key: str,
        request_timeout_s: int,
        task_model_map: Dict[str, str],
        default_quality: str = "gpt-4o",
    ) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._timeout = request_timeout_s
        self._task_models = {k.strip().lower(): v for k, v in (task_model_map or {}).items()}
        self._default_quality = default_quality

    def _model_for(self, task: str, override: Optional[str] = None) -> str:
        if override:
            return override
        key = (task or "").strip().lower()
        return self._task_models.get(key, self._default_quality)

    async def structured(
        self,
        *,
        task: str,
        system: str,
        user: str,
        schema_name: str,
        schema: Dict[str, Any],
        model_override: Optional[str] = None,
        timeout_s: Optional[int] = None,
        max_retries: int = 3,
    ) -> StructuredResult:
        """
        Generate JSON that MUST conform to the provided JSON Schema.
        """
        model = self._model_for(task, model_override)
        timeout = timeout_s or self._timeout

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        last_err: Exception | None = None
        for attempt in range(max_retries):
            try:
                resp = await self._client.responses.create(
                    model=model,
                    input=messages,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {"name": schema_name, "schema": schema},
                    },
                    timeout=timeout,
                )
                text = resp.output[0].content[0].text  # guaranteed JSON string for json_schema
                data = json.loads(text)
                return StructuredResult(data=data, model=model, raw=resp)
            except (RateLimitError, APITimeoutError, APIError) as e:
                last_err = e
                # simple exponential backoff: 0.5s, 1s, 2s...
                await asyncio.sleep(0.5 * (2 ** attempt))
                continue

        # If we exhausted retries, raise the last error
        if last_err:
            raise last_err
        raise RuntimeError("LLMClient.structured failed without an exception (unexpected)")

    async def aclose(self) -> None:
        """
        Placeholder for symmetry; AsyncOpenAI doesn't require explicit close.
        """
        return None