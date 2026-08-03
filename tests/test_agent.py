from collections.abc import Generator
from typing import Any

from forge_cli.core.agent import Agent
from forge_cli.providers.base import BaseProvider


class MockProvider(BaseProvider):
    def chat(self, context: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> Any:
        return "mock response"
        
    def stream(self, context: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> Generator[Any, None, None]:
        yield "mock "
        yield "response"

def test_agent_run():
    provider = MockProvider()
    agent = Agent(provider)
    result = agent.run([{"role": "user", "content": "hi"}])
    assert result == "mock response"

def test_agent_stream():
    provider = MockProvider()
    agent = Agent(provider)
    chunks = list(agent.stream_run([{"role": "user", "content": "hi"}]))
    assert "".join(chunks) == "mock response"
