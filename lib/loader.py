"""Load prompt definitions from YAML files."""
from pathlib import Path
from typing import Optional
import yaml

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

_CACHE: list[dict] | None = None


def _load_all_uncached() -> list[dict]:
    prompts = []
    for yaml_file in PROMPTS_DIR.rglob("*.yaml"):
        with open(yaml_file, encoding="utf-8") as f:
            try:
                prompt = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Failed to parse {yaml_file}: {e}") from e
        if not isinstance(prompt, dict):
            continue
        prompt["_path"] = str(yaml_file)
        prompt["_category_dir"] = yaml_file.parent.name
        prompts.append(prompt)
    return sorted(prompts, key=lambda p: (p.get("category", ""), p.get("title", "")))


def load_all_prompts(use_cache: bool = True) -> list[dict]:
    global _CACHE
    if use_cache and _CACHE is not None:
        return _CACHE
    _CACHE = _load_all_uncached()
    return _CACHE


def load_by_id(prompt_id: str) -> Optional[dict]:
    for prompt in load_all_prompts():
        if prompt.get("id") == prompt_id:
            return prompt
    return None


def load_by_category(category: str) -> list[dict]:
    return [p for p in load_all_prompts() if p.get("category") == category]


def list_categories() -> list[str]:
    return sorted({p.get("category", "") for p in load_all_prompts() if p.get("category")})


def invalidate_cache() -> None:
    global _CACHE
    _CACHE = None
