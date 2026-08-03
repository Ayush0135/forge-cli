from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: Optional[str] = None
    gemini_api_keys: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_api_keys: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_api_keys: Optional[str] = None

    default_provider: str = "gemini"
    default_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
