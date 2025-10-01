# app/core/config.py
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Paths ---
ROOT_DIR: Path = Path(__file__).resolve().parents[2]
CONFIG_DIR: Path = ROOT_DIR / "config"

# --- Env settings (env + .env) ---
class EnvSettings(BaseSettings):
    OPENAI_API_KEY: str = Field(default="")

    # Global defaults (used if YAMLs are missing fields)
    REQUEST_TIMEOUT_S: int = 45
    FAST_MODEL: str = "o3-mini"
    QUALITY_MODEL: str = "gpt-4o"

    # Optional overrides via nested env:
    #   TASK_MODELS__meal_plan=gpt-4o
    #   FEATURES__allow_model_override=true
    task_models: Dict[str, str] = Field(default_factory=dict)
    features: Dict[str, Any] = Field(default_factory=dict)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

env = EnvSettings()

# --- YAML helpers ---
def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            f"PyYAML is required to read {path}. Install with: pip install pyyaml"
        ) from e
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}

@lru_cache(maxsize=1)
def load_settings_file() -> Dict[str, Any]:
    return _read_yaml(CONFIG_DIR / "settings.yml")

@lru_cache(maxsize=1)
def load_features_file() -> Dict[str, Any]:
    return _read_yaml(CONFIG_DIR / "features.yml")

@lru_cache(maxsize=1)
def load_model_map_file() -> Dict[str, str]:
    data = _read_yaml(CONFIG_DIR / "model_map.yml")
    return {str(k).strip().lower(): str(v).strip() for k, v in data.items()}

# --- Public API ---
@lru_cache(maxsize=1)
def app_meta() -> Dict[str, Any]:
    s = load_settings_file()
    return {
        "name": s.get("app", {}).get("name", "Swasth Backend"),
        "env": s.get("app", {}).get("env", "dev"),
        "version": s.get("app", {}).get("version", "0.1.0"),
    }

@lru_cache(maxsize=1)
def server_config() -> Dict[str, Any]:
    s = load_settings_file()
    return s.get("server", {}) or {"host": "0.0.0.0", "port": 8000, "reload": True}

@lru_cache(maxsize=1)
def cors_config() -> Dict[str, Any]:
    s = load_settings_file()
    defaults = {
        "allow_origins": ["*"],
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "allow_credentials": True,
    }
    cfg = s.get("cors", {}) or {}
    return {**defaults, **cfg}

@lru_cache(maxsize=1)
def llm_defaults() -> Dict[str, Any]:
    s = load_settings_file()
    llm = s.get("llm", {}) or {}
    return {
        "request_timeout_s": llm.get("request_timeout_s", env.REQUEST_TIMEOUT_S),
        "fast_model": llm.get("fast_model", env.FAST_MODEL),
        "quality_model": llm.get("quality_model", env.QUALITY_MODEL),
    }

@lru_cache(maxsize=1)
def features() -> Dict[str, Any]:
    # file values then env overrides win
    merged = {**load_features_file(), **env.features}
    return merged

def feature_flag(name: str, default: Any | None = None) -> Any:
    return features().get(name, default)

@lru_cache(maxsize=1)
def model_map() -> Dict[str, str]:
    """
    Precedence: defaults < model_map.yml < env TASK_MODELS__*
    """
    defaults = {
        "meal_plan": llm_defaults()["quality_model"],
        "recipe": llm_defaults()["quality_model"],
        "grocery": llm_defaults()["fast_model"],
        "prakriti": llm_defaults()["fast_model"],
    }
    file_map = load_model_map_file()
    # Env overrides
    env_map = {str(k).lower(): str(v) for k, v in env.task_models.items()}
    merged = {**defaults, **file_map, **env_map}
    return merged

def model_for(task: str) -> str:
    key = task.strip().lower()
    return model_map().get(key, llm_defaults()["quality_model"])