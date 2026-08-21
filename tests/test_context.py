import time

from forge_cli.core.context import ContextEngine


def test_context_engine():
    engine = ContextEngine()
    
    # Give the async indexer a moment to build if cache is missing
    time.sleep(0.5)
    
    readme = engine.get_readme_summary()
    assert len(readme) > 0
    
    prompt = engine.build_system_prompt("find something")
    assert "REPOSITORY CONTEXT" in prompt
    assert "Project Tree" in prompt or "Relevant Code Symbols" in prompt
    assert "README Summary" in prompt


def test_symbol_store_indexing_and_fast_lookup():
    from forge_cli.core.parser import Symbol
    from forge_cli.core.symbols import SymbolStore

    store = SymbolStore()
    s1 = Symbol(name="MyClass", kind="class", file_path="a.py", start_line=1, end_line=10)
    s2 = Symbol(name="my_func", kind="function", file_path="b.py", start_line=1, end_line=5)
    s3 = Symbol(name="my_var", kind="variable", file_path="c.py", start_line=1, end_line=2)
    store.symbols = [s1, s2, s3]

    # Test fuzzy search (case-insensitive)
    matches = store.find_symbol("myclass")
    assert len(matches) == 1
    assert matches[0].name == "MyClass"

    # Test strict definition lookup O(1)
    defs = store.find_definition("my_func")
    assert len(defs) == 1
    assert defs[0].file_path == "b.py"

    # Test keyword deduplication in build_system_prompt
    engine = ContextEngine()
    engine.symbol_store.symbols = [s1, s2, s3]
    prompt = engine.build_system_prompt("find my_func and my_func with my_func")
    assert "my_func" in prompt
