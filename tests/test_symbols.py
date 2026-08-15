import tempfile
from pathlib import Path

from forge_cli.core.symbols import SymbolStore


def test_symbol_store_path_normalization_and_cache():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        py_file = tmp_path / "sample.py"
        py_file.write_text("class MyClass:\n    def my_func():\n        pass\n")

        store = SymbolStore(workspace_path=str(tmp_path))
        store.build_store(["sample.py"])

        symbols = store.find_symbol("MyClass")
        assert len(symbols) == 1
        assert symbols[0].file_path == "sample.py"

        # Test update_file
        py_file.write_text("class MyNewClass:\n    pass\n")
        store.update_file(str(py_file))

        assert len(store.find_symbol("MyClass")) == 0
        assert len(store.find_symbol("MyNewClass")) == 1

        # Test cache reloading
        new_store = SymbolStore(workspace_path=str(tmp_path))
        assert new_store.load_cache() is True
        assert len(new_store.find_symbol("MyNewClass")) == 1


def test_symbol_store_corrupted_cache():
    with tempfile.TemporaryDirectory() as tmp_dir:
        store = SymbolStore(workspace_path=str(tmp_dir))
        store.cache_file.write_text("invalid json content {{{")
        assert store.load_cache() is False
