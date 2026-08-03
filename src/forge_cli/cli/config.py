import json
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


def json_config_settings_source(*args, **kwargs) -> dict[str, Any]:
    """Loads configuration from ~/.forge/config.json if it exists."""
    config_path = Path.home() / ".forge" / "config.json"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}
    return {}

class Settings(BaseSettings):
    gemini_api_key: str | None = None
    gemini_api_keys: str | None = None
    openai_api_key: str | None = None
    openai_api_keys: str | None = None
    openrouter_api_key: str | None = None
    openrouter_api_keys: str | None = None

    default_provider: str = "gemini"
    default_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings, 
            json_config_settings_source, 
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

settings = Settings()
