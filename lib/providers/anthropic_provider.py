from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Calls the Anthropic Messages API.

    Uses TrackedAnthropic (cost tracking) if available in the local environment,
    otherwise falls back to the raw anthropic.Anthropic client.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self._client = None

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return "claude-sonnet-4-6"

    def _get_client(self):
        if self._client is None:
            try:
                # Prefer TrackedAnthropic when available (cost tracking)
                import sys
                sys.path.insert(0, str(__import__("pathlib").Path.home() / "Claude" / "intelligence-hub"))
                from utils.tracked_anthropic import TrackedAnthropic  # type: ignore
                self._client = TrackedAnthropic(api_key=self.api_key)
            except Exception:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_tokens: int = 1024,
    ) -> str:
        client = self._get_client()
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text
