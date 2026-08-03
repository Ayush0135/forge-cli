import pytest

from forge_cli.providers.factory import ProviderFactory
from forge_cli.providers.gemini import GeminiProvider
from forge_cli.providers.ollama import OllamaProvider
from forge_cli.providers.openai import OpenAIProvider


def test_factory_creates_gemini(mock_env: None) -> None:
    provider = ProviderFactory.create("gemini")
    assert isinstance(provider, GeminiProvider)
    assert provider.key_manager.get_key() == "test_gemini_key"


def test_factory_creates_openai(mock_env: None) -> None:
    provider = ProviderFactory.create("openai")
    assert isinstance(provider, OpenAIProvider)
    assert provider.key_manager.get_key() == "test_openai_key"


def test_factory_creates_ollama() -> None:
    provider = ProviderFactory.create("ollama")
    assert isinstance(provider, OllamaProvider)


def test_factory_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    from forge_cli.cli.config import settings

    monkeypatch.setattr(settings, "gemini_api_key", None)
    with pytest.raises(ValueError):
        ProviderFactory.create("gemini")
