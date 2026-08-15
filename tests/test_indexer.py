import tempfile
from pathlib import Path

from forge_cli.core.indexer import RepositoryIndexer


def test_indexer():
    indexer = RepositoryIndexer()
    indexer.build_index_sync()
    idx = indexer.get_index()
    assert "total_files" in idx
    assert "languages" in idx
    assert isinstance(idx["languages"], dict)


def test_indexer_ignores_and_large_files():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Ignored directory
        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        (venv_dir / "ignored.py").write_text("print('ignore me')")

        # Large file
        large_file = tmp_path / "package.json"
        large_file.write_text("{" + '"a": 1, ' * 1000000 + '"react": true}')

        # Normal file
        normal_file = tmp_path / "main.py"
        normal_file.write_text("print('hello')")

        indexer = RepositoryIndexer(workspace_path=str(tmp_path))
        indexer.build_index_sync()
        idx = indexer.get_index()

        tree = idx.get("tree", [])
        assert "main.py" in tree
        assert "package.json" in tree
        assert not any(".venv" in f for f in tree)


def test_indexer_corrupted_cache():
    with tempfile.TemporaryDirectory() as tmp_dir:
        indexer = RepositoryIndexer(workspace_path=str(tmp_dir))
        indexer.cache_file.write_text("{corrupted: true")
        indexer._load_cache()
        assert indexer.index == {}
