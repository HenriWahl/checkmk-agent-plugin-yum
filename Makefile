# Makefile for local development and CI convenience.
# Run `make help` to see available targets.

.PHONY: help lint lint-shell lint-python format typecheck test test-shell test-python build clean

SHELL := /bin/bash
PYTHON := python3

# Default target
help:
	@echo "Available targets:"
	@echo "  lint         Run all linters (shellcheck, ruff)"
	@echo "  lint-shell   Run shellcheck on shell scripts"
	@echo "  lint-python  Run ruff on Python code"
	@echo "  format       Format Python code with ruff"
	@echo "  typecheck    Run mypy type checker"
	@echo "  test         Run all tests"
	@echo "  test-shell   Run BATS shell tests"
	@echo "  test-python  Run pytest Python tests"
	@echo "  build        Build the MKP package (requires podman/docker)"
	@echo "  clean        Remove build artifacts"

# =============================================================================
# Linting
# =============================================================================

lint: lint-shell lint-python

lint-shell:
	@echo "==> Running shellcheck..."
	@if command -v shellcheck >/dev/null 2>&1; then \
		shellcheck agents/plugins/yum build/build-entrypoint.sh; \
	elif command -v podman >/dev/null 2>&1; then \
		podman run --rm -v "$$PWD:/mnt:Z" docker.io/koalaman/shellcheck-alpine:stable \
			shellcheck /mnt/agents/plugins/yum /mnt/build/build-entrypoint.sh; \
	elif command -v docker >/dev/null 2>&1; then \
		docker run --rm -v "$$PWD:/mnt" koalaman/shellcheck-alpine:stable \
			shellcheck /mnt/agents/plugins/yum /mnt/build/build-entrypoint.sh; \
	else \
		echo "ERROR: shellcheck, podman, or docker required"; exit 1; \
	fi

lint-python:
	@echo "==> Running ruff check..."
	ruff check lib/ build/build-modify-extension.py

format:
	@echo "==> Formatting Python code with ruff..."
	ruff format lib/ build/build-modify-extension.py
	ruff check --fix lib/ build/build-modify-extension.py

typecheck:
	@echo "==> Running mypy..."
	mypy --ignore-missing-imports build/build-modify-extension.py

# =============================================================================
# Testing
# =============================================================================

test: test-shell

test-shell:
	@echo "==> Running BATS tests..."
	bats tests/test_agent_yum.bats

test-python:
	@echo "==> Running pytest..."
	pytest tests/

# =============================================================================
# Building
# =============================================================================

build:
	@echo "==> Building MKP package..."
	@if command -v podman &>/dev/null; then \
		podman build -t checkmk-yum-build -f build/Dockerfile .; \
		podman run --rm -v "$$PWD:/source:Z" checkmk-yum-build; \
	elif command -v docker &>/dev/null; then \
		docker build -t checkmk-yum-build -f build/Dockerfile .; \
		docker run --rm -v "$$PWD:/source" checkmk-yum-build; \
	else \
		echo "ERROR: Neither podman nor docker found"; \
		exit 1; \
	fi

clean:
	@echo "==> Cleaning build artifacts..."
	rm -f *.mkp
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
