from typing import List, Optional

from forge_cli.cli.config import settings
from forge_cli.providers.base import BaseProvider
from forge_cli.providers.gemini import GeminiProvider
from forge_cli.providers.ollama import OllamaProvider
from forge_cli.providers.openai import OpenAIProvider
from forge_cli.utils.key_manager import RoundRobinKeyManager


def _get_keys(keys_str: Optional[str], key_str: Optional[str]) -> List[str]:
    raw = keys_str or key_str or ""
    return [k.strip() for k in raw.split(",") if k.strip()]


class ProviderFactory:
    @staticmethod
    def create(provider_name: Optional[str] = None, model: Optional[str] = None) -> BaseProvider:
        provider = provider_name or settings.default_provider

        if provider == "gemini":
            keys = _get_keys(settings.gemini_api_keys, settings.gemini_api_key)
            if not keys:
                raise ValueError("GEMINI_API_KEY is not set in environment or configuration.")
            return GeminiProvider(key_manager=RoundRobinKeyManager(keys), model=model or settings.default_model)

        elif provider == "openai":
            keys = _get_keys(settings.openai_api_keys, settings.openai_api_key)
            if not keys:
                raise ValueError("OPENAI_API_KEY is not set.")
            return OpenAIProvider(key_manager=RoundRobinKeyManager(keys), model=model or "gpt-4o")

        elif provider == "openrouter":
            keys = _get_keys(settings.openrouter_api_keys, settings.openrouter_api_key)
            if not keys:
                raise ValueError("OPENROUTER_API_KEY is not set.")
            return OpenAIProvider(
                key_manager=RoundRobinKeyManager(keys),
                model=model or "anthropic/claude-3-haiku",
                base_url="https://openrouter.ai/api/v1",
            )

        elif provider == "ollama":
            return OllamaProvider(model=model or "llama3")

        else:
            raise ValueError(f"Unknown provider: {provider}")
