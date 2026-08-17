## 2025-05-18 - SQLite session message index & primary key ordering
**Learning:** Querying foreign keys in SQLite without indexes leads to full table scans during message history retrieval. In SQLite, ordering by integer primary key `id ASC` is faster than timestamp string sorting and accurately preserves message insertion order.
**Action:** Always create indexes on foreign keys and frequently queried filter columns in SQLite schemas, and prefer primary key `id` sorting when chronological sequence matches insertion sequence.
