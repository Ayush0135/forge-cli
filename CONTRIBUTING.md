# Contributing to Forge CLI

First off, thank you for considering contributing to Forge CLI! It's people like you that make this tool great.

## Development Setup

1. **Prerequisites:** You need `uv` installed.
2. **Clone:**
   ```bash
   git clone https://github.com/Ayush0135/forge-cli.git
   cd forge-cli
   ```
3. **Install Dependencies:**
   ```bash
   uv sync
   uv pip install -e .
   ```

## Workflow

1. **Branch:** Create a branch for your feature or bugfix (`git checkout -b feature/my-new-feature`).
2. **Code:** Write your code, ensuring it follows the existing architecture pattern (modular, type-hinted).
3. **Test:** Run the test suite:
   ```bash
   uv run pytest
   ```
4. **Lint:** Ensure code complies with Ruff and Mypy:
   ```bash
   uv run ruff check .
   uv run mypy src tests
   ```
5. **Commit:** Commit your changes with descriptive messages.
6. **Push & Pull Request:** Push to your fork and submit a PR against the `main` branch.

## Adding New Tools
To add a new tool:
1. Create your tool logic in `src/forge_cli/tools/`.
2. Register the tool inside the `ToolManager` in `src/forge_cli/tools/manager.py` using `self.register()`.
3. Add a corresponding test in `tests/test_tools.py`.
