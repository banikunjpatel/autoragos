# llm/schema_registry.py
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Tuple

# Schemas live under: /schemas/*.json
ROOT_DIR: Path = Path(__file__).resolve().parents[1]
SCHEMAS_DIR: Path = ROOT_DIR.parent / "schemas"

# Default schema file per task
DEFAULT_SCHEMA_BY_TASK: Dict[str, str] = {
    "meal_plan": "meal_plan_family.json",
    "recipe": "recipe.json",
    "grocery": "grocery_list.json",
    "prakriti": "prakriti_assessment.json",
}


def _normalize_name(name: str) -> str:
    name = name.strip().lower()
    return name if name.endswith(".json") else f"{name}.json"


def _read_json(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=32)
def load_schema_file(filename: str) -> Dict:
    """
    Load and cache a schema JSON by filename (with or without .json extension).
    """
    fn = _normalize_name(filename)
    path = SCHEMAS_DIR / fn
    return _read_json(path)


def schema_by_name(name_or_filename: str) -> Tuple[str, Dict]:
    """
    Return (schema_name, schema_dict) for an explicit schema file name.
    schema_name is the file stem (without .json), used in Responses API.
    """
    fn = _normalize_name(name_or_filename)
    schema = load_schema_file(fn)
    return (Path(fn).stem, schema)


def schema_by_task(task: str) -> Tuple[str, Dict]:
    """
    Resolve the default schema for a logical task:
      'meal_plan' | 'recipe' | 'grocery' | 'prakriti'
    """
    key = task.strip().lower()
    if key not in DEFAULT_SCHEMA_BY_TASK:
        raise KeyError(f"No default schema registered for task '{task}'")
    return schema_by_name(DEFAULT_SCHEMA_BY_TASK[key])