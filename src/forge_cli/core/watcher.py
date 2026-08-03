from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from forge_cli.core.indexer import RepositoryIndexer
from forge_cli.core.symbols import SymbolStore
from forge_cli.utils.logger import logger


class ProjectWatcherEventHandler(FileSystemEventHandler):
    def __init__(self, indexer: RepositoryIndexer, symbol_store: SymbolStore):
        self.indexer = indexer
        self.symbol_store = symbol_store
        self.workspace_path = str(indexer.workspace_path)
        
    def _is_valid_file(self, path: str) -> bool:
        ignore_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", ".forge", "build", "dist"}
        path_obj = Path(path)
        
        for part in path_obj.parts:
            if part in ignore_dirs or (part.startswith(".") and part != ".github" and part != path_obj.name):
                return False
                
        ext = path_obj.suffix.lower()
        return ext in {".py", ".js", ".ts", ".tsx"}

    def on_modified(self, event):
        if event.is_directory:
            return
        if self._is_valid_file(event.src_path):
            logger.debug(f"File modified: {event.src_path}")
            self.symbol_store.update_file(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        if self._is_valid_file(event.src_path):
            logger.debug(f"File created: {event.src_path}")
            self.indexer.build_index_async()
            self.symbol_store.update_file(event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            return
        if self._is_valid_file(event.src_path):
            logger.debug(f"File deleted: {event.src_path}")
            self.indexer.build_index_async()
            self.symbol_store.update_file(event.src_path)

class ProjectWatcher:
    """Watches the workspace for file changes to update the cache asynchronously."""
    
    def __init__(self, indexer: RepositoryIndexer, symbol_store: SymbolStore):
        self.indexer = indexer
        self.symbol_store = symbol_store
        self.observer = Observer()
        self.handler = ProjectWatcherEventHandler(indexer, symbol_store)
        self.is_running = False

    def start(self):
        if self.is_running:
            return
        self.observer.schedule(self.handler, str(self.indexer.workspace_path), recursive=True)
        self.observer.start()
        self.is_running = True
        logger.info("Project file watcher started.")

    def stop(self):
        if not self.is_running:
            return
        self.observer.stop()
        self.observer.join()
        self.is_running = False
        logger.info("Project file watcher stopped.")
