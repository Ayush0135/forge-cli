## 2025-05-18 - SQLite Database Indexing for Session Memory
**Learning:** Querying `messages` filtered by `session_id` without an index causes full table scans in SQLite as message history accumulates across sessions. Adding `idx_messages_session_id` improves session message retrieval speed by ~66% (~3x faster).
**Action:** Always create indexes on foreign keys and frequently filtered columns (`session_id`) when setting up SQLite database schemas.
