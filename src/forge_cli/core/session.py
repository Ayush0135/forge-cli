import uuid
from typing import Any, Dict, List, Optional

from forge_cli.core.agent import Agent
from forge_cli.core.memory import MemorySystem
from forge_cli.providers.factory import ProviderFactory


class Session:
    def __init__(
        self, provider_name: Optional[str] = None, model: Optional[str] = None, session_id: Optional[str] = None
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

    def load_history(self) -> List[Dict[str, Any]]:
        return self.memory.get_messages(self.session_id)

    def get_context(self) -> List[Dict[str, Any]]:
        history = self.load_history()
        system_prompt = {
            "role": "system",
            "content": (
                "You are a helpful coding assistant. "
                "You have access to tools that allow you to read and write files. "
                "Always use these tools to inspect code before modifying it, "
                "and use the tools to apply your changes directly."
            )
        }
        if not history or history[0].get("role") != "system":
            return [system_prompt] + history
        return history

    def add_message(self, msg: Dict[str, Any]) -> None:
        self.memory.add_message(self.session_id, msg)

    def add_user_message(self, content: str) -> None:
        self.add_message({"role": "user", "content": content})

    def add_ai_message(self, content: str) -> None:
        self.add_message({"role": "assistant", "content": content})
