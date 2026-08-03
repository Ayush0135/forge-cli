import json
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
        self.cache_file = self.cache_dir / f"{self.workspace_path.name}_symbols.json"

    def build_store(self, files: list[str]):
        """Builds the symbol store from a list of files."""
        self.symbols = []
        for file in files:
            file_path = self.workspace_path / file
            if file_path.exists():
                self.symbols.extend(self.parser.parse_file(str(file_path)))
        self._save_cache()

    def update_file(self, file_path: str):
        """Updates the symbols for a single modified file."""
        # Remove old symbols for this file
        rel_path = str(Path(file_path).resolve())
        self.symbols = [s for s in self.symbols if s.file_path != rel_path]
        
        # Parse new
        if Path(file_path).exists():
            self.symbols.extend(self.parser.parse_file(file_path))
        self._save_cache()

    def find_symbol(self, query: str) -> list[Symbol]:
        """Fuzzy searches symbols by name or kind."""
        query_lower = query.lower()
        return [s for s in self.symbols if query_lower in s.name.lower() or query_lower in s.kind.lower()]

    def find_definition(self, symbol_name: str) -> list[Symbol]:
        """Finds strict definition of a symbol (class, function, method)."""
        valid_kinds = {"class", "function", "method", "variable"}
        return [s for s in self.symbols if s.name == symbol_name and s.kind in valid_kinds]

    def find_references(self, symbol_name: str) -> list[Symbol]:
        """Finds references (simplistic implementation based on text match within snippets)."""
        # A true AST reference finder requires more complex scope analysis, 
        # so this is a simplified semantic-light version.
        results = []
        for s in self.symbols:
            if s.code_snippet and symbol_name in s.code_snippet and s.name != symbol_name:
                results.append(s)
        return results

    def _save_cache(self):
        try:
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
            with open(self.cache_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to cache symbols: {e}")

    def load_cache(self) -> bool:
        if not self.cache_file.exists():
            return False
            
        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                
            self.symbols = [
                Symbol(
                    name=d["name"],
                    kind=d["kind"],
                    file_path=d["file_path"],
                    start_line=d["start_line"],
                    end_line=d["end_line"],
                    code_snippet=d.get("code_snippet")
                )
                for d in data
            ]
            return True
        except Exception:
            return False
