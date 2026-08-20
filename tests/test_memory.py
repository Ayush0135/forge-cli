import sqlite3

from forge_cli.core.memory import MemorySystem


def test_memory_init(temp_db_path: str) -> None:
    MemorySystem(db_path=temp_db_path)

    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "sessions" in tables
        assert "messages" in tables

        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        assert "idx_messages_session_id" in indexes
        assert "idx_sessions_created_at" in indexes


def test_memory_add_message(temp_db_path: str) -> None:
    memory = MemorySystem(db_path=temp_db_path)
    session_id = "test_session_1"

    memory.create_session(session_id, "test-model")
    memory.add_message(session_id, {"role": "user", "content": "Hello world"})

    messages = memory.get_messages(session_id)
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello world"
