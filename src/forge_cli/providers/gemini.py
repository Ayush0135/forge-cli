import json
from collections.abc import Generator
from typing import Any

import httpx

from forge_cli.providers.base import BaseProvider
from forge_cli.utils.key_manager import RoundRobinKeyManager
from forge_cli.utils.logger import logger


class GeminiProvider(BaseProvider):
    def __init__(self, key_manager: RoundRobinKeyManager, model: str = "gemini-2.5-flash"):
        self.key_manager = key_manager
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}"

    def _format_messages(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """Convert standard messages to Gemini format."""
        contents = []
        for msg in messages:
            if msg["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": msg.get("content", "")}]})
            elif msg["role"] == "assistant":
                if "tool_call" in msg:
                    contents.append({"role": "model", "parts": [{"functionCall": msg["tool_call"]}]})
                else:
                    contents.append({"role": "model", "parts": [{"text": msg.get("content", "")}]})
            elif msg["role"] == "tool":
                # For gemini, tool results are sent as 'function' role
                contents.append(
                    {
                        # v1beta supports function role for tool responses
                        "role": "user",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": msg.get("name", ""),
                                    "response": {"result": msg.get("content", "")},
                                }
                            }
                        ],
                    }
                )
        return {"contents": contents}

    def _prepare_payload(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        payload = self._format_messages(messages)
        if tools:
            # Gemini format for tools
            payload["tools"] = [{"functionDeclarations": tools}]
        return payload

    def chat(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> str | dict[str, Any]:
        payload = self._prepare_payload(messages, tools)
        headers = {"Content-Type": "application/json"}
        max_retries = len(self.key_manager.keys)
        last_error = None

        for attempt in range(max_retries):
            api_key = self.key_manager.get_key()
            url = f"{self.base_url}:generateContent?key={api_key}"

            try:
                with httpx.Client() as client:
                    response = client.post(url, json=payload, headers=headers, timeout=30.0)

                    if response.status_code == 429:
                        logger.warning(f"Rate limit hit for key ending in ...{api_key[-4:]}. Rotating...")
                        self.key_manager.next_key()
                        continue

                    response.raise_for_status()
                    data = response.json()

                    try:
                        part = data["candidates"][0]["content"]["parts"][0]
                        if "functionCall" in part:
                            return {
                                "type": "tool_call",
                                "name": part["functionCall"]["name"],
                                "args": part["functionCall"]["args"],
                            }
                        return str(part["text"])
                    except (KeyError, IndexError) as e:
                        logger.error(f"Failed to parse Gemini response: {data}")
                        return f"Error: Unexpected response format. {e}"
            except Exception as e:
                logger.error(f"Gemini API Error: {e!s}")
                last_error = e
                break

        return f"Error: {str(last_error) if last_error else 'All keys rate limited (429).'}"

    def stream(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> Generator[str | dict[str, Any], None, None]:
        payload = self._prepare_payload(messages, tools)
        headers = {"Content-Type": "application/json"}
        max_retries = len(self.key_manager.keys)

        for attempt in range(max_retries):
            api_key = self.key_manager.get_key()
            url = f"{self.base_url}:streamGenerateContent?alt=sse&key={api_key}"

            try:
                with httpx.Client() as client, client.stream("POST", url, json=payload, headers=headers, timeout=30.0) as response:
                        if response.status_code == 429:
                            logger.warning(f"Rate limit hit for key ending in ...{api_key[-4:]}. Rotating...")
                            self.key_manager.next_key()
                            for _ in response.iter_lines():
                                pass
                            continue

                        response.raise_for_status()
                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:]
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data = json.loads(data_str)
                                    part = data["candidates"][0]["content"]["parts"][0]
                                    if "functionCall" in part:
                                        yield {
                                            "type": "tool_call",
                                            "name": part["functionCall"]["name"],
                                            "args": part["functionCall"]["args"],
                                        }
                                        return
                                    yield part["text"]
                                except (KeyError, IndexError, json.JSONDecodeError):
                                    continue
                        return
            except Exception as e:
                logger.error(f"Gemini API Stream Error: {e!s}")
                yield f"\n[Error: {e!s}]"
                return

        yield "\n[Error: All keys rate limited (429).]"
