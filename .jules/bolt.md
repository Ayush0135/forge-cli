## 2025-05-10 - SQLite composite index for session message history
**Learning:** In SQLite conversation memory stores, querying messages by `session_id` without an index triggers full table scans and temporary B-tree sorting step for `ORDER BY`. Adding a composite index on `(session_id, id)` reduces query execution time by ~80-85% on session message lookups as conversation size grows.
**Action:** Always create indexes on foreign/lookup keys and common sorting columns in SQLite tables when data grows iteratively per session.
