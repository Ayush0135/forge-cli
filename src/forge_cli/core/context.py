import json
import re
import threading
from pathlib import Path

from forge_cli.core.indexer import RepositoryIndexer
from forge_cli.core.symbols import SymbolStore


class ContextEngine:
    """Builds intelligent repository context to avoid LLM context bloat."""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path).resolve()
        self.indexer = RepositoryIndexer(str(self.workspace_path))
        self.symbol_store = SymbolStore(str(self.workspace_path))
        
        # Trigger async index build if no cache
        self.indexer.build_index_async()
        
        if not self.symbol_store.load_cache():
            def build_symbols():
                idx = self.indexer.get_index()
                tree = idx.get("tree", [])
                valid_exts = {".py", ".js", ".ts", ".tsx"}
                parse_files = [f for f in tree if Path(f).suffix.lower() in valid_exts]
                self.symbol_store.build_store(parse_files)
            threading.Thread(target=build_symbols, daemon=True).start()

    def get_readme_summary(self) -> str:
        idx = self.indexer.get_index()
        important_files = idx.get("important_files", [])
        for f in important_files:
            if Path(f).name.lower() == "readme.md":
                try:
                    content = (self.workspace_path / f).read_text(encoding="utf-8")
                    return content[:800] + ("..." if len(content) > 800 else "")
                except Exception:
                    pass
        return "No README found."

    def build_system_prompt(self, user_prompt: str = "") -> str:
        """Compiles the system prompt dynamically based on the user prompt."""
        idx = self.indexer.get_index()
        
        keywords = re.findall(r'\b[A-Za-z0-9_]{3,}\b', user_prompt)
        
        relevant_symbols = []
        if self.symbol_store.symbols:
            for kw in keywords:
                if kw.lower() in {"find", "search", "the", "and", "how", "what", "where", "can", "you", "fix"}:
                    continue
                matches = self.symbol_store.find_symbol(kw)
                relevant_symbols.extend(matches[:3])
        
        unique_symbols = {s.name: s for s in relevant_symbols}.values()
        
        context_parts = [
            "You are Forge CLI, an advanced autonomous AI coding assistant.",
            "You have access to a suite of powerful tools.",
            "",
            "### REPOSITORY CONTEXT ###",
            f"Project: {idx.get('project_name', 'Unknown')}",
            f"Current Directory: {self.workspace_path}",
            f"Languages: {', '.join(idx.get('languages', {}).keys())}",
            f"Frameworks: {', '.join(idx.get('frameworks', []))}",
            "",
        ]
        
        if unique_symbols:
            context_parts.append("#### Relevant Code Symbols ####")
            for sym in unique_symbols:
                snippet = sym.code_snippet[:200] + "..." if sym.code_snippet and len(sym.code_snippet) > 200 else sym.code_snippet
                context_parts.append(f"- {sym.kind} `{sym.name}` in {sym.file_path}:{sym.start_line}")
                if snippet:
                    context_parts.append(f"  ```\n  {snippet}\n  ```")
            context_parts.append("")
        else:
            tree = idx.get('tree', [])
            context_parts.append("#### Project Tree (Partial) ####")
            context_parts.append("\n".join(tree[:50]))
            context_parts.append("")
            
        context_parts.extend([
            "#### README Summary ####",
            self.get_readme_summary(),
            "",
            "#### Git Status ####",
            json.dumps(idx.get("git_status", {})),
            "",
            "### RULES ###",
            "- Always use tools to inspect code before modifying.",
            "- Use the edit_file tool for precise patches rather than replacing entire files.",
            "- Execute shell commands safely using run_command."
        ])
        
        return "\n".join(context_parts)
