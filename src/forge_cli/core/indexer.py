import hashlib
import json
import os
import threading
from pathlib import Path
from typing import Any

from forge_cli.tools.git_tools import GitTools
from forge_cli.utils.logger import logger


class RepositoryIndexer:
    """Scans and caches metadata about the repository asynchronously."""

    # Maximum file size to inspect for configuration/framework detection (1 MB)
    MAX_FILE_READ_SIZE = 1 * 1024 * 1024
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path).resolve()
        self.cache_dir = Path.home() / ".forge" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        path_hash = hashlib.sha256(str(self.workspace_path).encode("utf-8")).hexdigest()[:12]
        self.cache_file = self.cache_dir / f"{self.workspace_path.name}_{path_hash}_index.json"
        self.index: dict[str, Any] = {}
        self.is_indexing = False
        self._lock = threading.Lock()

    def get_index(self) -> dict[str, Any]:
        """Returns the current index, loading from cache if necessary."""
        with self._lock:
            if not self.index:
                self._load_cache()
        if not self.index and not self.is_indexing:
            self.build_index_sync()
        return self.index

    def _load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.index = data
            except Exception as e:
                logger.warning(f"Failed to load index cache: {e}")

    def _save_cache(self):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.index, f)
        except Exception as e:
            logger.error(f"Failed to save index cache: {e}")

    def build_index_async(self):
        """Triggers indexing in a background daemon thread."""
        with self._lock:
            if self.is_indexing:
                return
        thread = threading.Thread(target=self.build_index_sync, daemon=True)
        thread.start()

    def build_index_sync(self):
        """Builds the repository index synchronously."""
        with self._lock:
            if self.is_indexing:
                return
            self.is_indexing = True
            
        try:
            logger.info("Starting repository indexing...")
            
            ignore_dirs = {
                ".git", ".venv", "venv", "node_modules", "__pycache__", ".forge",
                "build", "dist", ".idea", ".vscode", "target", ".next", ".nuxt",
                ".cache", "coverage", "__snapshots__", ".pytest_cache", ".mypy_cache",
                ".ruff_cache", "vendor", ".tox", "eggs"
            }
            
            file_tree = []
            extensions: dict[str, int] = {}
            total_size = 0
            important_files = []
            frameworks = set()
            package_managers = set()

            for root, dirs, files in os.walk(self.workspace_path):
                dirs[:] = [
                    d for d in dirs
                    if d not in ignore_dirs
                    and not d.endswith(".egg-info")
                    and (d == ".github" or not d.startswith("."))
                ]
                
                try:
                    rel_root = Path(root).relative_to(self.workspace_path)
                    str_rel_root = str(rel_root) if str(rel_root) != "." else ""
                except ValueError:
                    str_rel_root = ""
                
                for file in files:
                    if file.startswith(".") and file not in {".env", ".gitignore", ".env.example"}:
                        continue
                        
                    file_path = Path(root) / file
                    try:
                        if not file_path.is_file():
                            continue

                        size = file_path.stat().st_size
                        total_size += size
                        
                        ext = file_path.suffix.lower()
                        if ext:
                            extensions[ext] = extensions.get(ext, 0) + 1
                            
                        rel_path = str(Path(str_rel_root) / file) if str_rel_root else file
                        file_tree.append(rel_path)
                        
                        # Framework / Package manager detection
                        if file == "package.json":
                            package_managers.add("npm/yarn/pnpm")
                            important_files.append(rel_path)
                            if size <= self.MAX_FILE_READ_SIZE:
                                content = file_path.read_text(errors="ignore")
                                if "react" in content: frameworks.add("React")
                                if "next" in content: frameworks.add("Next.js")
                                if "vue" in content: frameworks.add("Vue")
                            
                        elif file in {"requirements.txt", "pyproject.toml"}:
                            package_managers.add("pip/uv")
                            important_files.append(rel_path)
                            if size <= self.MAX_FILE_READ_SIZE:
                                content = file_path.read_text(errors="ignore").lower()
                                if "django" in content: frameworks.add("Django")
                                if "fastapi" in content: frameworks.add("FastAPI")
                            
                        elif file == "Cargo.toml":
                            package_managers.add("cargo")
                            important_files.append(rel_path)
                            
                        elif file.lower() == "readme.md":
                            important_files.append(rel_path)
                            
                    except OSError:
                        pass
                        
            languages = {}
            if ".py" in extensions: languages["Python"] = extensions[".py"]
            if ".js" in extensions: languages["JavaScript"] = extensions[".js"]
            if ".ts" in extensions: languages["TypeScript"] = extensions[".ts"]
            if ".rs" in extensions: languages["Rust"] = extensions[".rs"]
            if ".go" in extensions: languages["Go"] = extensions[".go"]

            try:
                git_status = json.loads(GitTools.git_status(str(self.workspace_path)))
            except Exception:
                git_status = {}

            new_index = {
                "project_name": self.workspace_path.name,
                "project_root": str(self.workspace_path),
                "total_files": len(file_tree),
                "total_size_bytes": total_size,
                "languages": languages,
                "frameworks": list(frameworks),
                "package_managers": list(package_managers),
                "important_files": important_files,
                "git_status": git_status,
                "tree": file_tree
            }
            
            with self._lock:
                self.index = new_index
            self._save_cache()
            logger.info("Repository indexing complete.")
            
        finally:
            with self._lock:
                self.is_indexing = False
