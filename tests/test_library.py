"""Pytest coverage for the finance-ai-library core: loader + renderer.

No LLM API calls are made — rendering is checked against static example inputs.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from lib.loader import load_all_prompts, load_by_id  # noqa: E402
from lib.renderer import coerce_inputs, resolve_computed, render_template  # noqa: E402


def test_cli_list_returns_19_prompts():
    result = subprocess.run(
        [sys.executable, "cli.py", "list"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Total: 19 prompts" in result.stdout


def test_load_all_prompts_count():
    prompts = load_all_prompts(use_cache=False)
    assert len(prompts) == 19


@pytest.mark.parametrize("yaml_file", sorted(ROOT.glob("prompts/**/*.yaml")))
def test_each_yaml_parses_without_error(yaml_file):
    prompts = load_all_prompts(use_cache=False)
    matching = [p for p in prompts if p["_path"] == str(yaml_file)]
    assert len(matching) == 1
    prompt = matching[0]
    assert prompt.get("id"), f"{yaml_file} missing 'id'"
    assert prompt.get("title"), f"{yaml_file} missing 'title'"
    assert prompt.get("category"), f"{yaml_file} missing 'category'"
    assert prompt.get("system_prompt"), f"{yaml_file} missing 'system_prompt'"
    assert prompt.get("user_prompt_template"), f"{yaml_file} missing 'user_prompt_template'"


@pytest.mark.parametrize(
    "prompt_id",
    [
        "variance_commentary",
        "pl_deep_dive",
        "vat_rec",
        "headcount_forecast",
        "budget_reforecast",
    ],
)
def test_render_template_with_example_input(prompt_id):
    prompt = load_by_id(prompt_id)
    assert prompt is not None, f"prompt '{prompt_id}' not found"

    example_input = prompt.get("example_input")
    assert example_input, f"prompt '{prompt_id}' has no example_input"

    typed = coerce_inputs(prompt, example_input)
    resolved = resolve_computed(prompt, typed)
    rendered = render_template(prompt, resolved)

    assert isinstance(rendered, str)
    assert rendered.strip() != ""
    assert "{" not in rendered, f"unresolved placeholder left in rendered output: {rendered!r}"
