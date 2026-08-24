## 2025-05-10 - Skip synchronous disk JSON serialization in SymbolStore batch updates
**Learning:** `SymbolStore.update_file` synchronously rewrote the entire JSON symbol index file to disk on every file change. For high-frequency updates, disk IO introduced ~77ms overhead per update (~97% of total runtime). Adding `save_cache: bool = True` allows callers to skip intermediate writes.
**Action:** Always provide opt-in flags to defer synchronous disk writes when performing file/symbol updates in loops or batch background operations.
