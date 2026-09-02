"""Orchestrate: load → coerce → resolve → render → call → return."""
from .loader import load_by_id
from .renderer import coerce_inputs, resolve_computed, render_template
from .providers import LLMProvider


def render_only(prompt_id: str, raw_inputs: dict) -> tuple[str, str]:
    """Return (system_prompt, rendered_user_prompt) without calling any LLM.

    Useful for previewing the prompt before spending API credits.
    """
    prompt_def = load_by_id(prompt_id)
    if prompt_def is None:
        raise ValueError(f"Prompt '{prompt_id}' not found.")

    typed = coerce_inputs(prompt_def, raw_inputs)
    resolved = resolve_computed(prompt_def, typed)
    user_prompt = render_template(prompt_def, resolved)
    system_prompt = prompt_def.get("system_prompt", "")
    return system_prompt, user_prompt


def run_prompt(
    prompt_id: str,
    raw_inputs: dict,
    provider: LLMProvider,
    model: str | None = None,
    max_tokens: int = 1024,
) -> tuple[str, str, str]:
    """Run a prompt end-to-end.

    Returns (system_prompt, rendered_user_prompt, llm_response).
    """
    system_prompt, user_prompt = render_only(prompt_id, raw_inputs)
    resolved_model = model or provider.default_model
    response = provider.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=resolved_model,
        max_tokens=max_tokens,
    )
    return system_prompt, user_prompt, response


def run_prompt_from_def(
    prompt_def: dict,
    raw_inputs: dict,
    provider: LLMProvider,
    model: str | None = None,
    max_tokens: int = 1024,
) -> tuple[str, str, str]:
    """Run a prompt from an already-loaded definition (avoids re-lookup)."""
    typed = coerce_inputs(prompt_def, raw_inputs)
    resolved = resolve_computed(prompt_def, typed)
    user_prompt = render_template(prompt_def, resolved)
    system_prompt = prompt_def.get("system_prompt", "")
    resolved_model = model or provider.default_model
    response = provider.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=resolved_model,
        max_tokens=max_tokens,
    )
    return system_prompt, user_prompt, response
