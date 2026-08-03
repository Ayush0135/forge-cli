from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any


class BaseProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def chat(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> str | dict[str, Any]:
        """Send a chat request and return the full string response or a tool call dict."""

    @abstractmethod
    def stream(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> Generator[str | dict[str, Any], None, None]:
        """Send a chat request and yield the response stream or a tool call dict."""
