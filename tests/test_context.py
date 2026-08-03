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
