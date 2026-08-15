from pathlib import Path


class FileSystemTools:
    """Provides real file reading and writing capabilities for the agent."""

    @staticmethod
    def read_file(path: str) -> str:
        """Reads a file and returns its content."""
        try:
            p = Path(path).resolve()
            if not p.is_file():
                return f"Error: Path is not a file or does not exist: {path}"
            return p.read_text(encoding="utf-8")
        except OSError as e:
            return f"Error reading file {path}: {e!s}"

    @staticmethod
    def write_file(path: str, content: str) -> str:
        """Writes content to a new file, creating parent directories if needed. Do not use for editing existing files."""
        try:
            p = Path(path).resolve()
            if p.exists():
                return f"Error: File {path} already exists. Use edit_file to modify it."
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"Successfully wrote to {path}"
        except OSError as e:
            return f"Error writing to file {path}: {e!s}"

    @staticmethod
    def edit_file(path: str, action: str, target_text: str, replacement_text: str = "") -> str:
        """Safely edits an existing file."""
        try:
            p = Path(path).resolve()
            if not p.is_file():
                return f"Error: File {path} does not exist."
                
            content = p.read_text(encoding="utf-8")
            if target_text not in content:
                return "Error: target_text not found in file exactly as provided. Read the file to ensure whitespace matches perfectly."
                
            if action == "replace":
                new_content = content.replace(target_text, replacement_text, 1)
            elif action == "insert":
                separator = "" if target_text.endswith("\n") else "\n"
                new_content = content.replace(target_text, target_text + separator + replacement_text, 1)
            elif action == "delete":
                new_content = content.replace(target_text, "", 1)
            else:
                return "Error: action must be 'replace', 'insert', or 'delete'"
                
            p.write_text(new_content, encoding="utf-8")
            return f"Successfully applied '{action}' to {path}"
        except OSError as e:
            return f"Error editing file {path}: {e!s}"
