# AI Lab Linux CLI Utilities - Makefile
# Provides easy installation and development commands

.PHONY: help install uninstall dev-install test clean format lint docs

PYTHON := python3
PIP := pip3
INSTALL_PREFIX := /usr/local
PROJECT_DIR := $(shell pwd)

help: ## Show this help message
	@echo "AI Lab Linux CLI Utilities - Build Commands"
	@echo "==========================================="
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install system-wide (requires sudo)
	@echo "Installing AI Lab CLI Utilities system-wide..."
	@sudo ./install.sh

dev-install: ## Install in development mode
	@echo "Installing in development mode..."
	$(PIP) install -e .

uninstall: ## Uninstall from system (requires sudo)
	@echo "Uninstalling AI Lab CLI Utilities..."
	@sudo ./uninstall.sh

test: ## Run test suite
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v

test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	$(PYTHON) -m pytest tests/ --cov=src/linux_cli_utils --cov-report=html --cov-report=term

format: ## Format code with black
	@echo "Formatting code..."
	$(PYTHON) -m black src/ tests/

lint: ## Lint code with flake8
	@echo "Linting code..."
	$(PYTHON) -m flake8 src/ tests/

type-check: ## Type check with mypy
	@echo "Type checking..."
	$(PYTHON) -m mypy src/

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf htmlcov/
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

docs: ## Generate documentation
	@echo "Generating documentation..."
	@mkdir -p docs/
	@echo "# AI Lab CLI Utilities Documentation" > docs/README.md
	@echo "" >> docs/README.md
	@echo "## Commands" >> docs/README.md
	@$(PYTHON) -m linux_cli_utils.cli --help >> docs/CLI.md 2>/dev/null || echo "Run 'make dev-install' first"

build: ## Build distribution packages
	@echo "Building distribution packages..."
	$(PYTHON) -m build

dist: build ## Create distribution archive
	@echo "Creating distribution archive..."
	@tar -czf ailab-cli-utils-$(shell grep version pyproject.toml | cut -d'"' -f2).tar.gz --exclude-vcs .

check: lint type-check test ## Run all checks (lint, type-check, test)

dev-setup: ## Set up development environment
	@echo "Setting up development environment..."
	$(PIP) install -e ".[dev]"
	@echo "Development environment ready!"

quick-test: ## Run quick tests (no coverage)
	@echo "Running quick tests..."
	$(PYTHON) -m pytest tests/ -x -q

demo: dev-install ## Install and run demo commands
	@echo "AI Lab CLI Utilities - Demo"
	@echo "============================"
	@echo
	@echo "System Information:"
	@$(PYTHON) -m linux_cli_utils.sysinfo cpu
	@echo
	@echo "File Listing:"
	@$(PYTHON) -m linux_cli_utils.filemanager ls
	@echo
	@echo "Network Interfaces:"
	@$(PYTHON) -m linux_cli_utils.nettools interfaces

install-deps: ## Install all dependencies
	@echo "Installing dependencies..."
	$(PIP) install typer rich psutil click colorama pytest pytest-cov black flake8 mypy

# Development workflow targets
dev: dev-install test ## Development workflow: install and test

pre-commit: format lint test ## Pre-commit checks: format, lint, test

release: clean build ## Prepare release: clean and build

.DEFAULT_GOAL := help
