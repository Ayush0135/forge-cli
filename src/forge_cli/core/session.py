import uuid
from typing import Any

from forge_cli.core.agent import Agent
from forge_cli.core.context import ContextEngine
from forge_cli.core.memory import MemorySystem
from forge_cli.providers.factory import ProviderFactory


class Session:
    def __init__(
        self, provider_name: str | None = None, model: str | None = None, session_id: str | None = None
    ):
        self.memory = MemorySystem()
        self.provider = ProviderFactory.create(provider_name, model)
        self.agent = Agent(self.provider)

        if session_id:
            self.session_id = session_id
        else:
            self.session_id = str(uuid.uuid4())
            model_name = getattr(self.provider, "model", "unknown")
            self.memory.create_session(self.session_id, model_name)

    def load_history(self) -> list[dict[str, Any]]:
        return self.memory.get_messages(self.session_id)

    def get_context(self) -> list[dict[str, Any]]:
        history = self.load_history()
        engine = ContextEngine()
        system_prompt = {
            "role": "system",
            "content": engine.build_system_prompt()
        }
        if not history or history[0].get("role") != "system":
            return [system_prompt] + history
        
        # Always inject latest context
        history[0] = system_prompt
        return history

    def add_message(self, msg: dict[str, Any]) -> None:
        self.memory.add_message(self.session_id, msg)

    def add_user_message(self, content: str) -> None:
        self.add_message({"role": "user", "content": content})

    def add_ai_message(self, content: str) -> None:
        self.add_message({"role": "assistant", "content": content})
