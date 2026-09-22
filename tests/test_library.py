"""Pytest coverage for the finance-ai-library core: loader + renderer + runner.

No LLM API calls are made — rendering is checked against static example inputs,
and the runner orchestration path is exercised with a stub LLMProvider.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from lib.loader import load_all_prompts, load_by_id  # noqa: E402
from lib.renderer import coerce_inputs, resolve_computed, render_template  # noqa: E402
from lib.runner import render_only, run_prompt_from_def  # noqa: E402
from lib.providers.base import LLMProvider  # noqa: E402

ALL_PROMPTS = load_all_prompts(use_cache=False)
ALL_PROMPT_IDS = [p["id"] for p in ALL_PROMPTS]

REQUIRED_STRING_FIELDS = ["id", "title", "category", "difficulty", "system_prompt", "user_prompt_template"]
VALID_CATEGORIES = {"variance", "month_end", "reporting", "headcount", "costing"}
VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}


class StubProvider(LLMProvider):
    """Deterministic stand-in for a real LLM — never makes a network call."""

    def __init__(self):
        self.calls = []

    def complete(self, system_prompt: str, user_prompt: str, model: str, max_tokens: int = 1024) -> str:
        self.calls.append((system_prompt, user_prompt, model, max_tokens))
        return f"[stub response for model={model}, {len(user_prompt)} chars of user prompt]"

    @property
    def name(self) -> str:
        return "stub"

    @property
    def default_model(self) -> str:
        return "stub-default"


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
    assert len(ALL_PROMPTS) == 19


def test_no_duplicate_ids():
    assert len(ALL_PROMPT_IDS) == len(set(ALL_PROMPT_IDS))


@pytest.mark.parametrize("yaml_file", sorted(ROOT.glob("prompts/**/*.yaml")))
def test_each_yaml_matches_schema(yaml_file):
    """Every YAML file must satisfy the schema documented in CLAUDE.md."""
    prompts = load_all_prompts(use_cache=False)
    matching = [p for p in prompts if p["_path"] == str(yaml_file)]
    assert len(matching) == 1
    prompt = matching[0]

    for field in REQUIRED_STRING_FIELDS:
        assert prompt.get(field), f"{yaml_file} missing required '{field}'"

    assert prompt["id"] == yaml_file.stem, (
        f"{yaml_file}: id {prompt['id']!r} does not match filename stem {yaml_file.stem!r}"
    )
    assert prompt["category"] in VALID_CATEGORIES, f"{yaml_file}: invalid category {prompt['category']!r}"
    assert prompt["difficulty"] in VALID_DIFFICULTIES, f"{yaml_file}: invalid difficulty {prompt['difficulty']!r}"

    tags = prompt.get("tags")
    assert isinstance(tags, list) and tags, f"{yaml_file} missing/empty 'tags' list"

    inputs = prompt.get("inputs")
    assert isinstance(inputs, list) and inputs, f"{yaml_file} missing/empty 'inputs' list"
    for inp in inputs:
        for k in ("key", "label", "type"):
            assert k in inp, f"{yaml_file}: input {inp} missing '{k}'"

    assert "computed_fields" in prompt, f"{yaml_file} missing 'computed_fields' key (use {{}} if none)"
    assert isinstance(prompt["computed_fields"], dict), f"{yaml_file}: computed_fields must be a dict"

    assert prompt.get("output_spec"), f"{yaml_file} missing 'output_spec'"
    assert prompt.get("error_handling"), f"{yaml_file} missing 'error_handling'"


@pytest.mark.parametrize("prompt_id", ALL_PROMPT_IDS)
def test_example_input_covers_required_inputs(prompt_id):
    prompt = load_by_id(prompt_id)
    example_input = prompt.get("example_input")
    assert example_input, f"prompt '{prompt_id}' has no example_input"

    required_keys = {inp["key"] for inp in prompt.get("inputs", []) if inp.get("required")}
    missing = required_keys - example_input.keys()
    assert not missing, f"prompt '{prompt_id}' example_input missing required keys: {missing}"

    input_keys = {inp["key"] for inp in prompt.get("inputs", [])}
    unknown = example_input.keys() - input_keys
    assert not unknown, f"prompt '{prompt_id}' example_input has keys not declared in inputs: {unknown}"


@pytest.mark.parametrize("prompt_id", ALL_PROMPT_IDS)
def test_render_template_with_example_input(prompt_id):
    prompt = load_by_id(prompt_id)
    example_input = prompt.get("example_input")
    assert example_input, f"prompt '{prompt_id}' has no example_input"

    typed = coerce_inputs(prompt, example_input)
    resolved = resolve_computed(prompt, typed)
    rendered = render_template(prompt, resolved)

    assert isinstance(rendered, str)
    assert rendered.strip() != ""
    assert not re_unresolved(rendered), f"unresolved placeholder left in rendered output: {rendered!r}"


def re_unresolved(rendered: str) -> bool:
    import re
    return bool(re.search(r"\{[a-zA-Z_][a-zA-Z0-9_]*(:[^{}]*)?\}", rendered))


@pytest.mark.parametrize("prompt_id", ALL_PROMPT_IDS)
def test_computed_fields_evaluate_without_error(prompt_id):
    """Every computed_field expression must resolve to a non-None value against example_input."""
    prompt = load_by_id(prompt_id)
    computed = prompt.get("computed_fields") or {}
    if not computed:
        pytest.skip(f"'{prompt_id}' has no computed_fields")

    typed = coerce_inputs(prompt, prompt["example_input"])
    resolved = resolve_computed(prompt, typed)

    for field in computed:
        assert resolved.get(field) is not None, (
            f"prompt '{prompt_id}': computed_field '{field}' evaluated to None against example_input"
        )


@pytest.mark.parametrize("prompt_id", ALL_PROMPT_IDS)
def test_render_only_returns_system_and_user_prompt(prompt_id):
    prompt = load_by_id(prompt_id)
    system_prompt, user_prompt = render_only(prompt_id, prompt["example_input"])
    assert system_prompt.strip() != ""
    assert user_prompt.strip() != ""


@pytest.mark.parametrize("prompt_id", ALL_PROMPT_IDS)
def test_runner_orchestration_with_stub_provider(prompt_id):
    """run_prompt_from_def should wire render -> provider.complete -> response
    without ever touching a real network client.
    """
    prompt = load_by_id(prompt_id)
    stub = StubProvider()

    system_prompt, user_prompt, response = run_prompt_from_def(
        prompt_def=prompt,
        raw_inputs=prompt["example_input"],
        provider=stub,
        max_tokens=256,
    )

    assert len(stub.calls) == 1
    called_system, called_user, called_model, called_max_tokens = stub.calls[0]
    assert called_system == system_prompt == prompt.get("system_prompt", "")
    assert called_user == user_prompt
    assert called_model == stub.default_model
    assert called_max_tokens == 256
    assert response.startswith("[stub response")


def test_runner_orchestration_respects_explicit_model():
    prompt = load_by_id("variance_commentary")
    stub = StubProvider()
    run_prompt_from_def(
        prompt_def=prompt,
        raw_inputs=prompt["example_input"],
        provider=stub,
        model="some-explicit-model",
    )
    assert stub.calls[0][2] == "some-explicit-model"


def test_runner_raises_for_unknown_prompt_id():
    with pytest.raises(ValueError):
        render_only("this_prompt_does_not_exist", {})


@pytest.mark.parametrize("prompt_id", ALL_PROMPT_IDS)
def test_cli_info_and_preview_do_not_error(prompt_id):
    import json

    prompt = load_by_id(prompt_id)

    info_result = subprocess.run(
        [sys.executable, "cli.py", "info", prompt_id],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert info_result.returncode == 0, f"'info {prompt_id}' failed: {info_result.stderr}"

    preview_result = subprocess.run(
        [sys.executable, "cli.py", "preview", prompt_id, "--input", json.dumps(prompt["example_input"])],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert preview_result.returncode == 0, f"'preview {prompt_id}' failed: {preview_result.stderr}"
    assert not re_unresolved(preview_result.stdout), (
        f"'preview {prompt_id}' left unresolved placeholders: {preview_result.stdout!r}"
    )


def test_cli_list_filters_by_category():
    result = subprocess.run(
        [sys.executable, "cli.py", "list", "--category", "variance"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Total: 5 prompts" in result.stdout


def test_cli_info_unknown_prompt_exits_nonzero():
    result = subprocess.run(
        [sys.executable, "cli.py", "info", "not_a_real_prompt"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
