.PHONY: help install dev-install clean test lint format typecheck security docs all-checks
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

dev-install: ## Install development dependencies
	uv sync --all-extras --dev

clean: ## Clean cache files
	rm -rf .pytest_cache .ruff_cache .mypy_cache __pycache__ .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test: ## Run tests with coverage
	uv run pytest tests/ -v --cov=src --cov-report=term --cov-report=html

lint: ## Run linting
	uv run ruff check src/ tests/

format: ## Format code
	uv run ruff format src/ tests/

fix: ## Fix linting issues
	uv run ruff check --fix src/ tests/

typecheck: ## Run type checking
	uv run pyright src/ tests/

security: ## Run security checks
	uv run bandit -r src/
	uv run safety check

docs-coverage: ## Check documentation coverage
	uv run interrogate src/

dead-code: ## Check for dead code
	uv run vulture src/

pre-commit: ## Run pre-commit hooks
	uv run pre-commit run --all-files

all-checks: lint typecheck test security docs-coverage ## Run all quality checks
	@echo "All checks completed successfully!"

ci: all-checks ## Run CI pipeline locally

dev: dev-install pre-commit ## Set up development environment
	@echo "Development environment ready!"
