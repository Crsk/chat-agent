# Development Environment Setup
- **Python Version**: 3.13.5 via UV package manager
- **Package Manager**: UV for Python dependencies and version management

# Code Quality Tools
- **Linting/Formatting**: Ruff
  - Run: `uv run ruff check --fix src/ tests/`
  - Format: `uv run ruff format src/ tests/`
- **Type Checking**: Pyright (strict mode enabled)
  - Run: `uv run pyright src/ tests/`
- **Testing**: pytest with coverage
  - Run: `uv run pytest tests/ -v --cov=src`

# Pre-commit Hooks
- Installed and configured for automated quality checks
- Runs on every commit: Ruff linting/formatting + Pyright type checking
- Test manually: `uv run pre-commit run --all-files`

# Typing Best Practices
- All code uses strict typing with `from __future__ import annotations`
- Use modern type hints: `list[str]` not `List[str]`
- Proper generics with TypeVar, ParamSpec for functions/classes
- Protocol classes for structural typing
- Result types for error handling
