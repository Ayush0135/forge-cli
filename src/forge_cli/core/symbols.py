import hashlib
import json
import threading
from pathlib import Path

from forge_cli.core.parser import CodeParser, Symbol
from forge_cli.utils.logger import logger


class SymbolStore:
    """In-memory store for parsed symbols across the repository."""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path).resolve()
        self.parser = CodeParser()
        self.symbols: list[Symbol] = []
        self.cache_dir = Path.home() / ".forge" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        path_hash = hashlib.sha256(str(self.workspace_path).encode("utf-8")).hexdigest()[:12]
        self.cache_file = self.cache_dir / f"{self.workspace_path.name}_{path_hash}_symbols.json"
        self._lock = threading.Lock()

    def _normalize_path(self, file_path: str) -> str:
        p = Path(file_path)
        if not p.is_absolute():
            p = (self.workspace_path / p).resolve()
        else:
            p = p.resolve()
        try:
            return str(p.relative_to(self.workspace_path))
        except ValueError:
            return str(p)

    def _parse_and_normalize(self, full_path: Path) -> list[Symbol]:
        if not full_path.is_file():
            return []
        symbols = self.parser.parse_file(str(full_path))
        rel_str = self._normalize_path(str(full_path))
        for sym in symbols:
            sym.file_path = rel_str
            if sym.code_snippet and len(sym.code_snippet) > 1000:
                sym.code_snippet = sym.code_snippet[:1000] + "..."
        return symbols

    def build_store(self, files: list[str]):
        """Builds the symbol store from a list of files."""
        new_symbols = []
        for file in files:
            file_path = self.workspace_path / file
            if file_path.exists():
                new_symbols.extend(self._parse_and_normalize(file_path))

        with self._lock:
            self.symbols = new_symbols
        self._save_cache()

    def update_file(self, file_path: str):
        """Updates the symbols for a single modified file."""
        norm_path = self._normalize_path(file_path)
        full_path = Path(file_path).resolve()
        new_file_symbols = self._parse_and_normalize(full_path) if full_path.exists() else []

        with self._lock:
            self.symbols = [s for s in self.symbols if self._normalize_path(s.file_path) != norm_path]
            self.symbols.extend(new_file_symbols)

        self._save_cache()

    def find_symbol(self, query: str) -> list[Symbol]:
        """Fuzzy searches symbols by name or kind."""
        query_lower = query.lower()
        with self._lock:
            return [s for s in self.symbols if query_lower in s.name.lower() or query_lower in s.kind.lower()]

    def find_definition(self, symbol_name: str) -> list[Symbol]:
        """Finds strict definition of a symbol (class, function, method)."""
        valid_kinds = {"class", "function", "method", "variable"}
        with self._lock:
            return [s for s in self.symbols if s.name == symbol_name and s.kind in valid_kinds]

    def find_references(self, symbol_name: str) -> list[Symbol]:
        """Finds references (simplistic implementation based on text match within snippets)."""
        results = []
        with self._lock:
            for s in self.symbols:
                if s.code_snippet and symbol_name in s.code_snippet and s.name != symbol_name:
                    results.append(s)
        return results

    def _save_cache(self):
        try:
            with self._lock:
                data = [
                    {
                        "name": s.name,
                        "kind": s.kind,
                        "file_path": s.file_path,
                        "start_line": s.start_line,
                        "end_line": s.end_line,
                        "code_snippet": s.code_snippet
                    }
                    for s in self.symbols
                ]
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to cache symbols: {e}")

    def load_cache(self) -> bool:
        if not self.cache_file.exists():
            return False
            
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return False
                
            loaded = [
                Symbol(
                    name=d["name"],
                    kind=d["kind"],
                    file_path=d["file_path"],
                    start_line=d["start_line"],
                    end_line=d["end_line"],
                    code_snippet=d.get("code_snippet")
                )
                for d in data if isinstance(d, dict)
            ]
            with self._lock:
                self.symbols = loaded
            return True
        except Exception as e:
            logger.warning(f"Failed to load symbol cache: {e}")
            return False
