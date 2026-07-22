PYTHON := python
PIP := pip

.PHONY: help

help:
	@echo ""
	@echo "NDCA Build Targets"
	@echo "-----------------------------"
	@echo "make install"
	@echo "make lint"
	@echo "make format"
	@echo "make test"
	@echo "make clean"
	@echo ""

install:
	$(PIP) install -r requirements-dev.in

lint:
	ruff check src tests

format:
	black src tests

test:
	pytest -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache