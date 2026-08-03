from dataclasses import dataclass
from pathlib import Path

import tree_sitter
import tree_sitter_javascript
import tree_sitter_python
import tree_sitter_typescript

from forge_cli.utils.logger import logger


@dataclass
class Symbol:
    name: str
    kind: str  # class, function, method, variable, import, decorator
    file_path: str
    start_line: int
    end_line: int
    docstring: str | None = None
    code_snippet: str | None = None

class CodeParser:
    """Parses code files using Tree-sitter to extract symbols."""
    
    def __init__(self):
        try:
            self.langs = {
                "python": tree_sitter.Language(tree_sitter_python.language()),
                "javascript": tree_sitter.Language(tree_sitter_javascript.language()),
                "typescript": tree_sitter.Language(tree_sitter_typescript.language_typescript()),
            }
            self.parsers = {
                lang: tree_sitter.Parser(self.langs[lang]) for lang in self.langs
            }
        except Exception as e:
            logger.error(f"Failed to initialize tree-sitter: {e}")
            self.langs = {}
            self.parsers = {}

    def parse_file(self, file_path: str) -> list[Symbol]:
        """Parses a file and returns a list of extracted symbols."""
        path = Path(file_path)
        ext = path.suffix.lower()
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
        }
        
        if ext not in lang_map or lang_map[ext] not in self.parsers:
            return []
            
        lang = lang_map[ext]
        try:
            content = path.read_text(encoding="utf-8")
            if not content:
                return []
                
            tree = self.parsers[lang].parse(bytes(content, "utf-8"))
            return self._extract_symbols(tree, lang, str(path), content)
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return []

    def _extract_symbols(self, tree: tree_sitter.Tree, lang: str, file_path: str, content: str) -> list[Symbol]:
        symbols = []
        
        queries = {
            "python": """
                (class_definition name: (identifier) @class.name) @class.def
                (function_definition name: (identifier) @function.name) @function.def
                (import_statement) @import
                (import_from_statement) @import
                (decorator) @decorator
            """,
            "javascript": """
                (class_declaration name: (identifier) @class.name) @class.def
                (function_declaration name: (identifier) @function.name) @function.def
                (method_definition name: (property_identifier) @method.name) @method.def
                (variable_declarator name: (identifier) @variable.name) @variable.def
                (import_statement) @import
            """,
            "typescript": """
                (class_declaration name: (type_identifier) @class.name) @class.def
                (function_declaration name: (identifier) @function.name) @function.def
                (method_definition name: (property_identifier) @method.name) @method.def
                (variable_declarator name: (identifier) @variable.name) @variable.def
                (import_statement) @import
            """
        }
        
        if lang not in queries:
            return []
            
        try:
            query = tree_sitter.Query(self.langs[lang], queries[lang])
            cursor = tree_sitter.QueryCursor(query)
            matches = cursor.matches(tree.root_node)
            
            content_lines = content.splitlines()
            
            for _, match_dict in matches:
                for name, nodes in match_dict.items():
                    for node in nodes:
                        if name.endswith(".name"):
                            kind = name.split(".")[0]
                            parent = node.parent
                            if parent:
                                start = parent.start_point[0]
                                end = parent.end_point[0]
                                code_snippet = "\n".join(content_lines[start:end+1])
                                
                                symbols.append(Symbol(
                                    name=node.text.decode("utf-8") if node.text else "",
                                    kind=kind,
                                    file_path=file_path,
                                    start_line=start + 1,
                                    end_line=end + 1,
                                    code_snippet=code_snippet
                                ))
                        elif name in ["import", "decorator"]:
                            start = node.start_point[0]
                            end = node.end_point[0]
                            code_snippet = "\n".join(content_lines[start:end+1])
                            symbols.append(Symbol(
                                name=node.text.decode("utf-8") if node.text else "",
                                kind=name,
                                file_path=file_path,
                                start_line=start + 1,
                                end_line=end + 1,
                                code_snippet=code_snippet
                            ))
        except Exception as e:
            logger.error(f"Error extracting symbols in {file_path}: {e}")

        return symbols
