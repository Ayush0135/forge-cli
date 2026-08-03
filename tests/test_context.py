from forge_cli.core.context import ContextEngine


def test_context_engine():
    engine = ContextEngine()
    tree = engine.get_project_tree()
    assert "tests" in tree or "src" in tree
    
    readme = engine.get_readme_summary()
    assert len(readme) > 0
    
    prompt = engine.build_system_prompt()
    assert "REPOSITORY CONTEXT" in prompt
    assert "Project Tree" in prompt
    assert "README Summary" in prompt
