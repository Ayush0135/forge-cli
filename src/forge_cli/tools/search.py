import functools
import json
import os
import re
import subprocess

from forge_cli.core.symbols import SymbolStore

_IGNORE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".forge",
    "build", "dist", ".idea", ".vscode", "target", ".pytest_cache"
}

_BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".pdf", ".zip", ".gz",
    ".tar", ".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".pyd", ".so",
    ".dylib", ".dll", ".exe", ".bin", ".wasm", ".woff", ".woff2", ".ttf",
    ".eot", ".mp3", ".mp4"
}


class SearchTools:
    """Provides file and content search capabilities."""

    @staticmethod
    def search_symbol(query: str, path: str = ".") -> str:
        """Searches for parsed AST symbols."""
        store = SymbolStore(path)
        if not store.load_cache():
            return json.dumps({"error": "Symbol cache not ready. Run indexer first."})
            
        symbols = store.find_symbol(query)
        results = []
        for s in symbols[:50]:
            results.append({
                "name": s.name,
                "kind": s.kind,
                "file": s.file_path,
                "line": s.start_line
            })
        return json.dumps({"symbols": results, "total": len(symbols)})

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def _has_ripgrep() -> bool:
        """Cache ripgrep availability to avoid spawning subprocesses on every search call."""
        try:
            subprocess.run(["rg", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def search_code(query: str, path: str = ".", regex: bool = False) -> str:
        """Searches codebase for content."""
        if SearchTools._has_ripgrep():
            return SearchTools._rg_search_code(query, path, regex)
        else:
            return SearchTools._py_search_code(query, path, regex)

    @staticmethod
    def search_files(pattern: str, path: str = ".", regex: bool = False) -> str:
        """Searches codebase for files matching pattern."""
        if SearchTools._has_ripgrep():
            return SearchTools._rg_search_files(pattern, path, regex)
        else:
            return SearchTools._py_search_files(pattern, path, regex)

    @staticmethod
    def _rg_search_code(query: str, path: str, regex: bool) -> str:
        cmd = ["rg", "--json"]
        if not regex:
            cmd.append("--fixed-strings")
        cmd.extend([query, path])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 2:
                return json.dumps({"error": result.stderr})
            
            matches = []
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if data["type"] == "match":
                        matches.append({
                            "file": data["data"]["path"]["text"],
                            "line_number": data["data"]["line_number"],
                            "content": data["data"]["lines"]["text"].strip()
                        })
                except json.JSONDecodeError:
                    pass
            return json.dumps({"matches": matches[:100], "total": len(matches)})
        except OSError as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def _rg_search_files(pattern: str, path: str, regex: bool) -> str:
        cmd = ["rg", "--files", "--hidden", "-g", f"*{pattern}*" if not regex else pattern, path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 2:
                return json.dumps({"error": result.stderr})
            
            files = [f for f in result.stdout.splitlines() if f.strip()]
            return json.dumps({"files": files[:100], "total": len(files)})
        except OSError as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def _py_search_code(query: str, path: str, regex: bool) -> str:
        matches = []
        compiled_regex = None
        if regex:
            try:
                # Use re.MULTILINE so ^ and $ match line boundaries in whole-content search
                compiled_regex = re.compile(query, re.MULTILINE)
            except re.error as e:
                return json.dumps({"error": f"Invalid regex: {e!s}"})

        max_file_size = 10 * 1024 * 1024  # 10 MB limit for text search

        for root, dirs, files in os.walk(path):
            dirs[:] = [
                d for d in dirs
                if d not in _IGNORE_DIRS and not (d.startswith(".") and d != ".github")
            ]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in _BINARY_EXTENSIONS:
                    continue
                file_path = os.path.join(root, file)
                try:
                    if os.path.getsize(file_path) > max_file_size:
                        continue

                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # OPTIMIZATION: Early content pre-filtering via fast C-level string/regex search
                    # avoids line-by-line enumeration and splitlines on non-matching files (~25x speedup).
                    if regex and compiled_regex:
                        if not compiled_regex.search(content):
                            continue
                        for i, line in enumerate(content.splitlines(), 1):
                            if compiled_regex.search(line):
                                matches.append({
                                    "file": file_path,
                                    "line_number": i,
                                    "content": line.strip()
                                })
                    else:
                        if query not in content:
                            continue
                        for i, line in enumerate(content.splitlines(), 1):
                            if query in line:
                                matches.append({
                                    "file": file_path,
                                    "line_number": i,
                                    "content": line.strip()
                                })
                except (OSError, UnicodeDecodeError):
                    continue
        return json.dumps({"matches": matches[:100], "total": len(matches)})

    @staticmethod
    def _py_search_files(pattern: str, path: str, regex: bool) -> str:
        files_found = []
        compiled_regex = None
        if regex:
            try:
                compiled_regex = re.compile(pattern)
            except re.error as e:
                return json.dumps({"error": f"Invalid regex: {e!s}"})

        for root, dirs, files in os.walk(path):
            dirs[:] = [
                d for d in dirs
                if d not in _IGNORE_DIRS and not (d.startswith(".") and d != ".github")
            ]
            for file in files:
                match_found = False
                if regex and compiled_regex:
                    if compiled_regex.search(file):
                        match_found = True
                else:
                    if pattern in file:
                        match_found = True

                if match_found:
                    files_found.append(os.path.join(root, file))

        return json.dumps({"files": files_found[:100], "total": len(files_found)})
