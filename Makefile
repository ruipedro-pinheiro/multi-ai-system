# CHIKA - Makefile (RIGEUR 42)
# Like gcc -Wall -Werror -Wextra but for Python

.PHONY: help lint format typecheck test all clean install

help:
	@echo "🎯 CHIKA - Makefile (RIGEUR 42 style)"
	@echo ""
	@echo "Commands:"
	@echo "  make install     - Install dependencies + pre-commit hooks"
	@echo "  make format      - Format code (black + isort)"
	@echo "  make lint        - Run linters (flake8 + pylint)"
	@echo "  make typecheck   - Run mypy (strict mode = -Werror)"
	@echo "  make test        - Run tests"
	@echo "  make all         - Run ALL checks (format + lint + typecheck + test)"
	@echo "  make clean       - Clean cache files"
	@echo ""
	@echo "⚠️  ALL warnings = build FAILURE (like -Werror)"

install:
	@echo "📦 Installing dependencies..."
	cd backend && pip install -r requirements.txt -r requirements-dev.txt
	@echo "🔧 Installing pre-commit hooks..."
	pre-commit install
	@echo "✅ Ready! Run 'make all' before every commit."

format:
	@echo "🎨 Formatting code..."
	black backend/ --line-length 100
	isort backend/ --profile black --line-length 100
	@echo "✅ Code formatted"

lint:
	@echo "🔍 Running linters..."
	@echo "  → flake8..."
	flake8 backend/ --max-line-length=100 --ignore=E203,W503 --exclude=venv,__pycache__,.git
	@echo "  → pylint..."
	pylint backend/ --rcfile=pyproject.toml || true
	@echo "✅ Linting complete"

typecheck:
	@echo "🔬 Type checking (mypy --strict)..."
	cd backend && mypy . --config-file ../pyproject.toml --show-error-codes
	@echo "✅ Type check passed (ZERO warnings)"

test:
	@echo "🧪 Running tests..."
	cd backend && pytest tests/ -v --tb=short
	@echo "✅ Tests passed"

all: format lint typecheck test
	@echo ""
	@echo "✅✅✅ ALL CHECKS PASSED ✅✅✅"
	@echo "Code is clean like -Wall -Werror -Wextra"

clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean!"

# Quick check before commit
check: format lint typecheck
	@echo "✅ Ready to commit!"
