# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project Overview
This is a chat agent application built with LangGraph workflow management, using OpenRouter/OpenAI APIs for LLM interactions. The architecture follows a modular design with clear separation between chat logic, CLI interface, and configuration.

## Core Architecture
- **Chat Module** (`src/chat/`): Core chat functionality with LangGraph workflow
  - `workflow.py`: StateGraph-based chat workflow with conditional edges
  - `models.py`: TypedDict data models (ChatMessage, ChatState)
  - `llm_client.py`: OpenRouter API client implementation
  - `message_handler.py`: Message processing logic
  - `config.py`: Configuration management with environment variable handling
- **CLI Module** (`src/cli/`): Command-line interface for interactive chat
  - `chat_runner.py`: Interactive chat session management

## Key Dependencies
- **LangGraph**: Workflow management and state graphs
- **LangChain**: LLM integration framework
- **OpenAI SDK**: API client for OpenRouter/OpenAI
- **python-dotenv**: Environment variable management

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
- **Security**: Bandit for security issues
  - Run: `uv run bandit -r src/`
- **Documentation**: Interrogate for docstring coverage
  - Run: `uv run interrogate src/`
- **Dead Code**: Vulture for unused code detection
  - Run: `uv run vulture src/`
- **Vulnerability Scanning**: Safety for dependency vulnerabilities
  - Run: `uv run safety check`

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

# Code Structure Guidelines
- **NO __init__.py files in src/**: Avoid package initialization files in source code to keep structure simple (init files in tests/ are OK)
- **Direct imports**: Use explicit module paths like `from src.chat.models import ChatState`
- **Feature-based organization**: Group related functionality in focused directories
- **Single responsibility**: Each module should have one clear purpose

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
