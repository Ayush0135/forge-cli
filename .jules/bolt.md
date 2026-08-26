## 2025-08-26 - Whole-File Regex Pre-filtering with Line Anchors
**Learning:** When pre-filtering full file content strings using `re.compile` before line iteration, regex patterns using line anchors (`^` or `$`) will fail unless compiled with `re.MULTILINE`.
**Action:** Always include `re.MULTILINE` when compiling regex objects that pre-search full text file contents before line-by-line scanning.
