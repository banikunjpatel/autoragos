# llm/prompt_renderer.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

# Prompts live under: /prompts/<task>/v{version}.j2
ROOT_DIR: Path = Path(__file__).resolve().parents[1]
PROMPTS_DIR: Path = ROOT_DIR.parent / "prompts"

_env = Environment(
    loader=FileSystemLoader(str(PROMPTS_DIR)),
    autoescape=select_autoescape(disabled_extensions=("j2",)),
    trim_blocks=True,
    lstrip_blocks=True,
)


def template_name(task: str, version: int) -> str:
    """
    Compute relative template path inside /prompts based on task + version.
      e.g., task='meal_plan', version=1 -> 'meal_plan/v1.j2'
    """
    safe_task = task.strip().lower().replace(" ", "_")
    return f"{safe_task}/v{int(version)}.j2"


def render_prompt(task: str, version: int, context: Dict[str, Any]) -> str:
    """
    Render a Jinja2 prompt by task and version with the provided context.
    Raises TemplateNotFound with a clear message if missing.
    """
    name = template_name(task, version)
    try:
        tpl = _env.get_template(name)
    except TemplateNotFound as e:
        raise TemplateNotFound(
            f"Prompt template not found: '{name}'. "
            f"Expected at: {PROMPTS_DIR / name}"
        ) from e

    text = tpl.render(**(context or {}))

    # Normalize whitespace: strip trailing whitespace at ends; keep internal newlines
    return text.strip() + "\n"
