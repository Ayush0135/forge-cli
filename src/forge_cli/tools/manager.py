import json
import traceback
from collections.abc import Callable
from typing import Any

from forge_cli.tools.filesystem import FileSystemTools
from forge_cli.tools.git_tools import GitTools
from forge_cli.tools.search import SearchTools
from forge_cli.tools.shell import ShellTools
from forge_cli.utils.logger import logger


class ToolManager:
    """Manages tool registration, validation, and safe execution."""
    
    def __init__(self):
        self.tools: dict[str, dict[str, Any]] = {}
        self._register_default_tools()
        
    def _register_default_tools(self):
        self.register(
            name="read_file",
            func=FileSystemTools.read_file,
            description="Reads a file and returns its content. Use this to inspect code before modifying.",
            parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
        )
        self.register(
            name="write_file",
            func=FileSystemTools.write_file,
            description="Writes content to a new file. Overwrites are protected.",
            parameters={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}
        )
        self.register(
            name="edit_file",
            func=FileSystemTools.edit_file,
            description="Safely edits a file via patch insertion/replacement/deletion.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "action": {"type": "string", "enum": ["replace", "insert", "delete"]},
                    "target_text": {"type": "string", "description": "Exact text block to find."},
                    "replacement_text": {"type": "string", "description": "Text to insert/replace."}
                },
                "required": ["path", "action", "target_text"]
            }
        )
        self.register(
            name="run_command",
            func=ShellTools.run_command,
            description="Executes a shell command.",
            parameters={"type": "object", "properties": {"command": {"type": "string"}, "cwd": {"type": "string"}}, "required": ["command"]}
        )
        self.register(
            name="search_code",
            func=SearchTools.search_code,
            description="Searches codebase for a string or regex.",
            parameters={"type": "object", "properties": {"query": {"type": "string"}, "path": {"type": "string"}, "regex": {"type": "boolean"}}, "required": ["query"]}
        )
        self.register(
            name="search_files",
            func=SearchTools.search_files,
            description="Searches for files by pattern.",
            parameters={"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}, "regex": {"type": "boolean"}}, "required": ["pattern"]}
        )
        self.register(
            name="search_symbol",
            func=SearchTools.search_symbol,
            description="Searches AST parsed symbols (classes, functions, etc.).",
            parameters={"type": "object", "properties": {"query": {"type": "string"}, "path": {"type": "string"}}, "required": ["query"]}
        )
        self.register(
            name="git_status",
            func=GitTools.git_status,
            description="Returns current git status.",
            parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": []}
        )
        self.register(
            name="git_diff",
            func=GitTools.git_diff,
            description="Returns git diff.",
            parameters={"type": "object", "properties": {"path": {"type": "string"}, "staged": {"type": "boolean"}}, "required": []}
        )
        self.register(
            name="git_log",
            func=GitTools.git_log,
            description="Returns recent git commits.",
            parameters={"type": "object", "properties": {"path": {"type": "string"}, "max_count": {"type": "integer"}}, "required": []}
        )
        self.register(
            name="git_branch",
            func=GitTools.git_branch,
            description="Returns git branches.",
            parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": []}
        )

    def register(self, name: str, func: Callable, description: str, parameters: dict[str, Any]):
        """Registers a tool with its schema."""
        self.tools[name] = {
            "func": func,
            "schema": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }

    def get_schemas(self) -> list[dict[str, Any]]:
        """Returns schemas for all registered tools."""
        return [tool["schema"] for tool in self.tools.values()]

    def execute(self, name: str, args: Any) -> str:
        """Safely executes a tool by name."""
        if name not in self.tools:
            error_msg = f"Error: Tool '{name}' not found."
            logger.warning(error_msg)
            return error_msg

        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}

        if not isinstance(args, dict):
            args = {}
            
        logger.info(f"Tool Execute: {name}", extra={"tool_args": args})
        try:
            result = self.tools[name]["func"](**args)
            return str(result)
        except Exception as e:
            error_msg = f"Tool '{name}' failed: {e!s}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
