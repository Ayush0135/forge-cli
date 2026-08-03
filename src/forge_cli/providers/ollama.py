import json
from typing import Any, Dict, Generator, List, Optional, Union

import httpx

from forge_cli.providers.base import BaseProvider
from forge_cli.utils.logger import logger


class OllamaProvider(BaseProvider):
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def chat(
        self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None
    ) -> Union[str, Dict[str, Any]]:
        url = f"{self.base_url}/api/chat"
        payload = {"model": self.model, "messages": messages, "stream": False}

        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return str(data["message"]["content"])
        except Exception as e:
            logger.error(f"Ollama API Error: {str(e)}")
            return f"Error: {str(e)}"

    def stream(
        self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None
    ) -> Generator[Union[str, Dict[str, Any]], None, None]:
        url = f"{self.base_url}/chat"
        payload = {"model": self.model, "messages": messages, "stream": True}

        try:
            with httpx.Client() as client:
                with client.stream("POST", url, json=payload, timeout=30.0) as response:
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
            logger.error(f"Ollama API Stream Error: {str(e)}")
            yield f"\n[Error: {str(e)}]"
