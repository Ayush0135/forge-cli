from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, Optional, Union


class BaseProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def chat(
        self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None
    ) -> Union[str, Dict[str, Any]]:
        """Send a chat request and return the full string response or a tool call dict."""
        pass

    @abstractmethod
    def stream(
        self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None
    ) -> Generator[Union[str, Dict[str, Any]], None, None]:
        """Send a chat request and yield the response stream or a tool call dict."""
        pass
