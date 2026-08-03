from pathlib import Path

from forge_cli.tools.git_tools import GitTools


class ContextEngine:
    """Builds intelligent repository context to avoid LLM context bloat."""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path).resolve()

    def get_project_tree(self, max_depth: int = 3) -> str:
        """Returns a condensed directory tree structure."""
        ignore_dirs = {".git", ".venv", "node_modules", "__pycache__", ".forge", "build", "dist", ".idea", ".vscode"}
        
        tree_lines = []
        
        def walk(current_path: Path, depth: int):
            if depth > max_depth:
                return
                
            try:
                items = sorted(current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
                for item in items:
                    if item.name in ignore_dirs or (item.name.startswith(".") and item.name != ".github"):
                        continue
                        
                    indent = "  " * depth
                    if item.is_dir():
                        tree_lines.append(f"{indent}📁 {item.name}/")
                        walk(item, depth + 1)
                    else:
                        tree_lines.append(f"{indent}📄 {item.name}")
            except OSError:
                # A repository may contain unreadable files or directories.
                return
                
        tree_lines.append(f"📁 {self.workspace_path.name}/")
        walk(self.workspace_path, 1)
        return "\n".join(tree_lines)

    def get_readme_summary(self) -> str:
        """Attempts to read the README.md."""
        for name in ["README.md", "README.txt", "readme.md"]:
            p = self.workspace_path / name
            if p.exists():
                try:
                    content = p.read_text(encoding="utf-8")
                    return content[:800] + ("..." if len(content) > 800 else "")
                except (OSError, UnicodeDecodeError):
                    continue
        return "No README found."

    def get_git_status(self) -> str:
        """Returns the current git status."""
        return GitTools.git_status(str(self.workspace_path))

    def build_system_prompt(self) -> str:
        """Compiles the system prompt with all context."""
        context_parts = [
            "You are Forge CLI, an advanced autonomous AI coding assistant.",
            "You have access to a suite of powerful tools.",
            "",
            "### REPOSITORY CONTEXT ###",
            f"Current Directory: {self.workspace_path}",
            "",
            "#### Project Tree ####",
            self.get_project_tree(),
            "",
            "#### README Summary ####",
            self.get_readme_summary(),
            "",
            "#### Git Status ####",
            self.get_git_status(),
            "",
            "### RULES ###",
            "- Always use tools to inspect code before modifying.",
            "- Use the edit_file tool for precise patches rather than replacing entire files.",
            "- Execute shell commands safely using run_command."
        ]
        
        return "\n".join(context_parts)
