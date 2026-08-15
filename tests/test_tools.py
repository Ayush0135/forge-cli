import json

from forge_cli.tools.git_tools import GitTools
from forge_cli.tools.manager import ToolManager
from forge_cli.tools.search import SearchTools
from forge_cli.tools.shell import ShellTools


def test_shell_tool():
    result = ShellTools.run_command("echo hello")
    data = json.loads(result)
    assert "hello" in data["stdout"]
    assert data["exit_code"] == 0

def test_search_tool():
    result = SearchTools.search_code("def test_search_tool", path="tests")
    data = json.loads(result)
    assert "error" not in data
    
def test_git_tool():
    result = GitTools.git_status()
    data = json.loads(result)
    assert "branch" in data or "error" in data

def test_tool_manager():
    manager = ToolManager()
    schemas = manager.get_schemas()
    assert len(schemas) > 5
    
    result = manager.execute("run_command", {"command": "echo test"})
    assert "test" in result

def test_filesystem_insert():
    import tempfile
    from pathlib import Path

    from forge_cli.tools.filesystem import FileSystemTools

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("line 1\nline 2\n", encoding="utf-8")

        # Test insert on line ending with \n
        res = FileSystemTools.edit_file(str(test_file), "insert", "line 1\n", "inserted line")
        assert "Successfully applied" in res
        content = test_file.read_text(encoding="utf-8")
        assert "line 1\ninserted line" in content
        assert "line 1\n\ninserted line" not in content
