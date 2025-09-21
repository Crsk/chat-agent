# Chat Agent Starter Template

A template for building chat agent applications with LangGraph workflow management and OpenRouter/OpenAI API integration.

## Features

- **LangGraph Workflow**: StateGraph-based chat workflow with conditional edges
- **OpenRouter Integration**: Flexible LLM provider support via OpenRouter API
- **CLI Interface**: Interactive command-line chat interface
- **Type Safety**: Strict typing with Pyright
- **Code Quality**: Pre-commit hooks with Ruff linting and formatting

## Quick Start

1. **Use this template**: Click "Use this template" to create a new repository
2. **Clone your repository**:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```
3. **Set up environment**:
   ```bash
   # Install UV if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   uv sync
   ```
4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenRouter API key
   ```
5. **Run the chat agent**:
   ```bash
   uv run python main.py
   ```

## Development

- **Lint/Format**: `uv run ruff check --fix src/ tests/ && uv run ruff format src/ tests/`
- **Type Check**: `uv run pyright src/ tests/`
- **Test**: `uv run pytest tests/ -v --cov=src`
- **All Checks**: `uv run pre-commit run --all-files`

## Architecture

- `src/chat/`: Core chat functionality with LangGraph workflow
- `src/cli/`: Command-line interface
- `tests/`: Test suite
