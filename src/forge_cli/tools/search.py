import json
import os
import re
import subprocess

from forge_cli.core.symbols import SymbolStore


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
    def _has_ripgrep() -> bool:
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
        ignore_dirs = {".git", ".venv", "node_modules", "__pycache__"}
        
        compiled_regex = None
        if regex:
            try:
                compiled_regex = re.compile(query)
            except re.error as e:
                return json.dumps({"error": f"Invalid regex: {e!s}"})

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            match_found = False
                            if regex and compiled_regex:
                                if compiled_regex.search(line):
                                    match_found = True
                            else:
                                if query in line:
                                    match_found = True
                                    
                            if match_found:
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
        ignore_dirs = {".git", ".venv", "node_modules", "__pycache__"}
        
        compiled_regex = None
        if regex:
            try:
                compiled_regex = re.compile(pattern)
            except re.error as e:
                return json.dumps({"error": f"Invalid regex: {e!s}"})

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
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
