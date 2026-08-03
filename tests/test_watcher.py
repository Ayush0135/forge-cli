from forge_cli.core.indexer import RepositoryIndexer
from forge_cli.core.symbols import SymbolStore
from forge_cli.core.watcher import ProjectWatcher


def test_watcher_init():
    indexer = RepositoryIndexer()
    store = SymbolStore()
    watcher = ProjectWatcher(indexer, store)
    assert not watcher.is_running
