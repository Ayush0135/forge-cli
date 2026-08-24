import tempfile
from pathlib import Path

from forge_cli.core.indexer import RepositoryIndexer
from forge_cli.core.symbols import SymbolStore


def test_indexer():
    indexer = RepositoryIndexer()
    indexer.build_index_sync()
    idx = indexer.get_index()
    assert "total_files" in idx
    assert "languages" in idx
    assert isinstance(idx["languages"], dict)


def test_symbol_store_update_file_save_cache_flag():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        store = SymbolStore(workspace_path=str(tmpdir))
        store.cache_file = tmp_path / "cache.json"

        # Update file without saving to cache
        store.update_file(str(test_file), save_cache=False)
        assert len(store.symbols) == 1
        assert store.symbols[0].name == "hello"
        assert not store.cache_file.exists()

        # Update file with saving to cache
        store.update_file(str(test_file), save_cache=True)
        assert len(store.symbols) == 1
        assert store.cache_file.exists()
