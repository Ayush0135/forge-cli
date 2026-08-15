import json
import sqlite3
from pathlib import Path
from typing import Any


class MemorySystem:
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            self.base_dir = Path.home() / ".forge"
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = self.base_dir / "memory.db"
        else:
            self.db_path = Path(db_path)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass
        return conn

    def _init_db(self) -> None:
        """Initialize the SQLite database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)
            conn.commit()

    def create_session(self, session_id: str, model: str) -> None:
        """Create a new session."""
        with self._get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO sessions (session_id, model) VALUES (?, ?)", (session_id, model))
            conn.commit()

    def add_message(self, session_id: str, message: dict[str, Any]) -> None:
        """Add a full message dictionary to a session."""
        role = message.get("role", "unknown")
        content = json.dumps(message)
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content)
            )
            conn.commit()

    def get_messages(self, session_id: str) -> list[dict[str, Any]]:
        """Retrieve all messages for a given session."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC, id ASC", (session_id,)
            )
            messages = []
            for row in cursor.fetchall():
                try:
                    msg = json.loads(row["content"])
                    messages.append(msg)
                except json.JSONDecodeError:
                    # Legacy fallback for old rows
                    messages.append({"role": row["role"], "content": row["content"]})
            return messages

    def get_latest_session_id(self) -> str | None:
        """Get the ID of the most recent session."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT session_id FROM sessions ORDER BY created_at DESC, id DESC LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else None
