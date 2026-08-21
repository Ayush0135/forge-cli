## 2025-03-01 - ContextEngine Symbol Search Bottleneck
**Learning:** `ContextEngine.build_system_prompt()` extracts prompt keywords and calls `SymbolStore.find_symbol()` on each word. When prompts contain repeated tokens or common stopwords, redundant $O(N)$ symbol array scans were executed on every user prompt, repeatedly performing `s.name.lower()` string allocations.
**Action:** Deduplicate prompt keywords before querying symbols, expand stopwords set, and pre-compute lowercased tuples plus a name index in `SymbolStore` for O(1) definition lookups.
