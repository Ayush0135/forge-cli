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
    assert len(data["matches"]) > 0

def test_search_tool_regex_multiline():
    result = SearchTools.search_code("^def test_search_tool", path="tests", regex=True)
    data = json.loads(result)
    assert "error" not in data
    assert len(data["matches"]) > 0

def test_search_files_dotfile():
    result = SearchTools.search_files(".env.example", path=".")
    data = json.loads(result)
    assert "error" not in data
    assert len(data["files"]) > 0
    
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
