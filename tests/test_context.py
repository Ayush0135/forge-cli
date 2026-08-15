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

def test_context_engine_symbol_deduplication():
    engine = ContextEngine()
    # Mock duplicate symbol names with different file paths/lines
    from forge_cli.core.parser import Symbol
    engine.symbol_store.symbols = [
        Symbol(name="test_func", kind="function", file_path="a.py", start_line=1, end_line=5),
        Symbol(name="test_func", kind="function", file_path="b.py", start_line=10, end_line=15),
    ]
    prompt = engine.build_system_prompt("test_func")
    assert "a.py:1" in prompt
    assert "b.py:10" in prompt
