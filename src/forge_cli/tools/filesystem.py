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
        except Exception as e:
            return f"Error reading file {path}: {str(e)}"

    @staticmethod
    def write_file(path: str, content: str) -> str:
        """Writes content to a file, creating parent directories if needed."""
        try:
            p = Path(path).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing to file {path}: {str(e)}"
