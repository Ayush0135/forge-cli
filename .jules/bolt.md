## 2025-05-18 - Avoid `pathlib.Path` inside high-frequency `os.walk` loops
**Learning:** Instantiating `pathlib.Path` objects and calling methods like `Path.relative_to` or `Path.stat()` inside `os.walk` loops across thousands of files introduces substantial memory allocation and string-parsing overhead in Python.
**Action:** In directory traversal hot loops, prefer direct `os.path` functions (`os.path.relpath`, `os.path.getsize`, `os.path.splitext`) and string operations to achieve ~3x faster execution.
