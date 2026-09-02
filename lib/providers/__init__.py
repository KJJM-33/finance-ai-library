from .base import LLMProvider
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider


def create_provider(
    provider: str,
    api_key: str,
    base_url: str | None = None,
) -> LLMProvider:
    """Factory: create an LLM provider by name.

    provider: "anthropic" | "openai" | "openai_compatible"
    base_url: only used for openai_compatible (e.g. http://localhost:11434/v1)
    """
    if provider == "anthropic":
        return AnthropicProvider(api_key=api_key)
    if provider in ("openai", "openai_compatible"):
        return OpenAIProvider(api_key=api_key, base_url=base_url)
    raise ValueError(
        f"Unknown provider '{provider}'. "
        "Valid options: 'anthropic', 'openai', 'openai_compatible'."
    )


__all__ = ["LLMProvider", "AnthropicProvider", "OpenAIProvider", "create_provider"]
