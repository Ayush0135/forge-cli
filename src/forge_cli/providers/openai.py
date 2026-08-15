import json
from collections.abc import Generator
from typing import Any

import httpx

from forge_cli.providers.base import BaseProvider
from forge_cli.utils.key_manager import RoundRobinKeyManager
from forge_cli.utils.logger import logger


class OpenAIProvider(BaseProvider):
    def __init__(
        self, key_manager: RoundRobinKeyManager, model: str = "gpt-4o", base_url: str = "https://api.openai.com/v1"
    ):
        self.key_manager = key_manager
        self.model = model
        self.base_url = base_url

    def _format_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        formatted = []
        for msg in messages:
            if msg["role"] == "user" or (msg["role"] == "assistant" and "tool_call" not in msg):
                formatted.append({"role": msg["role"], "content": msg.get("content", "")})
            elif msg["role"] == "assistant" and "tool_call" in msg:
                tc = msg["tool_call"]
                args = tc.get("args", {})
                args_str = json.dumps(args) if isinstance(args, dict) else str(args)
                formatted.append(
                    {
                        "role": "assistant",
                        "content": msg.get("content", "") or None,
                        "tool_calls": [
                            {
                                "id": tc.get("id", "call_123"),
                                "type": "function",
                                "function": {
                                    "name": tc["name"],
                                    "arguments": args_str,
                                },
                            }
                        ],
                    }
                )
            elif msg["role"] == "tool":
                formatted.append(
                    {
                        "role": "tool",
                        "tool_call_id": msg.get("id", "call_123"),
                        "content": str(msg.get("content", "")),
                    }
                )
        return formatted

    def _prepare_payload(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        payload = {"model": self.model, "messages": self._format_messages(messages)}
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]
        return payload

    def chat(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> str | dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        payload = self._prepare_payload(messages, tools)

        max_retries = len(self.key_manager.keys)
        last_error = None

        for attempt in range(max_retries):
            api_key = self.key_manager.get_key()
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

            try:
                with httpx.Client() as client:
                    response = client.post(url, json=payload, headers=headers, timeout=30.0)

                    if response.status_code == 429:
                        logger.warning(f"Rate limit hit for key ending in ...{api_key[-4:]}. Rotating...")
                        self.key_manager.next_key()
                        continue

                    response.raise_for_status()
                    data = response.json()
                    message = data["choices"][0]["message"]

                    if message.get("tool_calls"):
                        tc = message["tool_calls"][0]
                        return {
                            "type": "tool_call",
                            "id": tc.get("id", "call_123"),
                            "name": tc["function"]["name"],
                            "args": json.loads(tc["function"]["arguments"]),
                        }
                    return str(message.get("content", ""))
            except Exception as e:
                logger.error(f"OpenAI API Error: {e!s}")
                last_error = e
                break

        return f"Error: {str(last_error) if last_error else 'All keys rate limited (429).'}"

    def stream(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> Generator[str | dict[str, Any], None, None]:
        url = f"{self.base_url}/chat/completions"
        payload = self._prepare_payload(messages, tools)
        payload["stream"] = True

        max_retries = len(self.key_manager.keys)

        for attempt in range(max_retries):
            api_key = self.key_manager.get_key()
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

            try:
                with httpx.Client() as client, client.stream("POST", url, json=payload, headers=headers, timeout=30.0) as response:
                        if response.status_code == 429:
                            logger.warning(f"Rate limit hit for key ending in ...{api_key[-4:]}. Rotating...")
                            self.key_manager.next_key()
                            for _ in response.iter_lines():
                                pass
                            continue

                        response.raise_for_status()

                        tool_call_name = None
                        tool_call_id = None
                        tool_call_args = ""
                        is_tool_call = False

                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:]
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data = json.loads(data_str)
                                    delta = data["choices"][0].get("delta", {})

                                    if delta.get("tool_calls"):
                                        is_tool_call = True
                                        tc = delta["tool_calls"][0]
                                        if tc.get("id"):
                                            tool_call_id = tc["id"]
                                        if "function" in tc:
                                            func = tc["function"]
                                            if func.get("name"):
                                                tool_call_name = func["name"]
                                            if func.get("arguments"):
                                                tool_call_args += func["arguments"]
                                    elif delta.get("content"):
                                        yield delta["content"]
                                except (KeyError, IndexError, json.JSONDecodeError):
                                    continue

                        if is_tool_call:
                            try:
                                parsed_args = json.loads(tool_call_args) if tool_call_args else {}
                            except json.JSONDecodeError:
                                parsed_args = {}
                            yield {
                                "type": "tool_call",
                                "name": tool_call_name,
                                "args": parsed_args,
                                "id": tool_call_id or "call_123",
                            }
                        return
            except Exception as e:
                logger.error(f"OpenAI API Stream Error: {e!s}")
                yield f"\n[Error: {e!s}]"
                return

        yield "\n[Error: All keys rate limited (429).]"
