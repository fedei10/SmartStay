from pathlib import Path

import yaml

from app.core.config import BASE_DIR


PROMPT_FILE = BASE_DIR / "app" / "coreAgents" / "config" / "prompt_templates.yaml"


def load_prompt_templates() -> dict:
    with Path(PROMPT_FILE).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_prompt(prompt_name: str) -> str:
    templates = load_prompt_templates()
    prompt_templates = templates.get("prompt_templates", {})

    try:
        return prompt_templates[prompt_name]
    except KeyError as exc:
        available = list(prompt_templates.keys())
        raise ValueError(
            f"Prompt '{prompt_name}' not found. Available prompts: {available}"
        ) from exc
