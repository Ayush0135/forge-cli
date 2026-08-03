import os
import tempfile

from forge_cli.core.parser import CodeParser


def test_python_parser():
    parser = CodeParser()
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("class TestClass:\n    def method(self):\n        pass\n")
        path = f.name
    
    try:
        symbols = parser.parse_file(path)
        assert len(symbols) >= 2
        assert any(s.name == "TestClass" and s.kind == "class" for s in symbols)
        assert any(s.name == "method" and s.kind == "function" for s in symbols)
    finally:
        os.remove(path)
