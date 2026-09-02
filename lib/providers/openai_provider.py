from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """Calls any OpenAI-compatible chat completions endpoint.

    Covers: OpenAI, Azure OpenAI, Ollama, Groq, Mistral, Together, Anyscale, etc.
    Set base_url to the provider's endpoint (e.g. http://localhost:11434/v1 for Ollama).
    For a local Ollama instance with no auth, pass api_key="ollama".
    """

    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self._client = None

    @property
    def name(self) -> str:
        return "openai_compatible"

    @property
    def default_model(self) -> str:
        return "gpt-4o"

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            kwargs: dict = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_tokens: int = 1024,
    ) -> str:
        client = self._get_client()
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
