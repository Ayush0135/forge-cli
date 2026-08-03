from typing import Any

from forge_cli.tools.filesystem import FileSystemTools


def get_tool_schemas() -> list[dict[str, Any]]:
    """Returns the JSON schemas for all available tools."""
    return [
        {
            "name": "read_file",
            "description": "Reads a file and returns its content. Use this to inspect code before modifying.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "The absolute or relative path to the file."}},
                "required": ["path"],
            },
        },
        {
            "name": "write_file",
            "description": "Writes content to a file. Overwrites existing files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The path to the file."},
                    "content": {"type": "string", "description": "The text content to write into the file."},
                },
                "required": ["path", "content"],
            },
        },
    ]


def execute_tool(name: str, args: dict[str, Any]) -> str:
    """Executes a tool by name and returns the string observation."""
    if name == "read_file":
        return FileSystemTools.read_file(args.get("path", ""))
    elif name == "write_file":
        return FileSystemTools.write_file(args.get("path", ""), args.get("content", ""))
    else:
        return f"Error: Unknown tool {name}"
