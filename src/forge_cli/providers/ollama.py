import json
from collections.abc import Generator
from typing import Any

import httpx

from forge_cli.providers.base import BaseProvider
from forge_cli.utils.logger import logger


class OllamaProvider(BaseProvider):
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def chat(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> str | dict[str, Any]:
        url = f"{self.base_url}/api/chat"
        payload = {"model": self.model, "messages": messages, "stream": False}

        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return str(data["message"]["content"])
        except Exception as e:
            logger.error(f"Ollama API Error: {e!s}")
            return f"Error: {e!s}"

    def _format_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "tool":
                formatted.append({"role": "user", "content": f"[Tool Result for {msg.get('name', 'tool')}]: {content}"})
            else:
                formatted.append({"role": role, "content": str(content)})
        return formatted

    def stream(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> Generator[str | dict[str, Any], None, None]:
        url = f"{self.base_url}/api/chat"
        payload = {"model": self.model, "messages": self._format_messages(messages), "stream": True}

        try:
            with httpx.Client() as client, client.stream("POST", url, json=payload, timeout=30.0) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    yield data["message"]["content"]
                                if data.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Ollama API Stream Error: {e!s}")
            yield f"\n[Error: {e!s}]"
