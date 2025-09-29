# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

boa-restrictor is a custom Python and Django linter developed by Ambient Digital. It provides a collection of linting rules that enforce code quality and style guidelines specific to Python and Django projects.

## Architecture

### Core Components

- **CLI Module** (`boa_restrictor/cli/`): Entry point and configuration handling
  - `main.py`: Main CLI logic that processes files and runs linting rules
  - `configuration.py`: Loads and manages pyproject.toml configuration
  - `utils.py`: Utility functions for parsing source code

- **Rules System** (`boa_restrictor/rules/`): Plugin-based linting rules
  - `python/`: Python-specific linting rules (prefix: PBR)
  - `django/`: Django-specific linting rules (prefix: DBR)
  - Base `Rule` class in `common/rule.py` that all rules inherit from

- **Common Utilities** (`boa_restrictor/common/`):
  - `rule.py`: Base Rule class with AST processing
  - `noqa.py`: Handles `# noqa` comment parsing for rule exclusions

- **Projections** (`boa_restrictor/projections/`):
  - `occurrence.py`: Data structure for linting violations

### Rule System Design

All linting rules inherit from the base `Rule` class and follow this pattern:
- Each rule has a unique `RULE_ID` (e.g., "PBR001", "DBR001")
- Rules process Python AST (Abstract Syntax Tree) to detect violations
- Rules return `Occurrence` objects containing violation details
- Rules can be excluded globally, per-file, or per-line via `# noqa` comments

## Development Commands

### Testing
```bash
# Run all tests
pytest --ds settings tests

# Run tests with coverage
coverage run -m pytest tests
coverage report -m

# Run a specific test
pytest tests/rules/python/test_asterisk_required.py
```

### Linting and Formatting
```bash
# Run pre-commit hooks on all files
pre-commit run --all-files

# Run specific hooks
pre-commit run ruff --all-files
pre-commit run ruff-format --all-files
```

### Setup for Development
```bash
# Install dependencies
pip install -U pip-tools
pip-compile --extra dev -o requirements.txt pyproject.toml --resolver=backtracking
pip-sync

# Install pre-commit hooks
pre-commit install -t pre-push -t pre-commit --install-hooks
```

### Documentation
```bash
# Build documentation
sphinx-build docs/ docs/_build/html/
```

### Publishing
```bash
# Publish to PyPI
flit publish

# Publish to TestPyPI
flit publish --repository testpypi
```

## Configuration

The linter is configured via `pyproject.toml` under the `[tool.boa-restrictor]` section:
- `exclude`: List of rule IDs to exclude globally
- `enable_django_rules`: Boolean to enable/disable Django-specific rules
- `per-file-excludes`: Dictionary mapping file patterns to excluded rule IDs

## Adding New Rules

1. Create a new rule class inheriting from `Rule` in the appropriate subdirectory
2. Implement the `check()` method to return `Occurrence` objects
3. Add the rule to the appropriate tuple in `rules/__init__.py`
4. Write comprehensive tests in the corresponding test file
5. Update rule documentation as needed

## Testing Strategy

- Each rule has dedicated test files in `tests/rules/`
- Tests use pytest with Django settings
- Tests verify both positive (violation detected) and negative (no violation) cases
- Use AST parsing to test rule logic against code snippets
