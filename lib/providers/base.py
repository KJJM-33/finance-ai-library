from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Vendor-agnostic interface for LLM text completion."""

    @abstractmethod
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_tokens: int = 1024,
    ) -> str:
        """Return the model's text response."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'anthropic', 'openai')."""

    @property
    @abstractmethod
    def default_model(self) -> str:
        """The model to use when none is specified."""
