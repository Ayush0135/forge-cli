import os
import tempfile
from collections.abc import Generator

import pytest

from forge_cli.cli.config import settings


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "gemini_api_key", "test_gemini_key")
    monkeypatch.setattr(settings, "openai_api_key", "test_openai_key")
