from forge_cli.core.indexer import RepositoryIndexer


def test_indexer():
    indexer = RepositoryIndexer()
    indexer.build_index_sync()
    idx = indexer.get_index()
    assert "total_files" in idx
    assert "languages" in idx
    assert isinstance(idx["languages"], dict)
