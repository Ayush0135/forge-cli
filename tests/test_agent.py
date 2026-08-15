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


class ToolMockProvider(BaseProvider):
    def __init__(self):
        self.called = False

    def chat(self, context: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> Any:
        if not self.called:
            self.called = True
            return {"type": "tool_call", "name": "run_command", "args": {"command": "echo tool_called"}}
        return "tool execution completed"

    def stream(self, context: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> Generator[Any, None, None]:
        if not self.called:
            self.called = True
            yield {"type": "tool_call", "name": "run_command", "args": {"command": "echo tool_called"}}
        else:
            yield "tool execution completed"


def test_agent_run_with_tools():
    provider = ToolMockProvider()
    agent = Agent(provider)
    context = [{"role": "user", "content": "run command"}]
    res = agent.run(context)
    assert res == "tool execution completed"
    assert len(context) == 4
    assert context[2]["role"] == "tool"
    assert "tool_called" in context[2]["content"]


def test_agent_stream_with_tools():
    provider = ToolMockProvider()
    agent = Agent(provider)
    context = [{"role": "user", "content": "run command"}]
    chunks = list(agent.stream_run(context))
    assert any("Executing tool" in c for c in chunks)
    assert "tool execution completed" in "".join(chunks)
