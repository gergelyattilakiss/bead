# Bead Development Guide

## Build/Test/Lint Commands
- **Run all tests:** `tox` or `pytest`
- **Run single test:** `pytest path/to/test_file.py::TestClass::test_method`
- **Run tests with coverage:** `pytest --cov=. --cov-report=term-missing`
- **Lint code:** `flake8 bead bead_cli tests`
- **Type check:** `mypy --ignore-missing-imports bead bead_cli tests`
- **Build executables:** `make executables`
- **Quick test script:** `dev/test` (runs flake8, mypy, and pytest)

## Code Style Guidelines
- **Max line length:** 99 characters
- **Ignored flake8 rules:** W503, W504, E251, E241, E221, E722
- **Import style:** Group stdlib, third-party, local imports; use relative imports within packages
- **String formatting:** Use f-strings for Python 3.10+ compatibility
- **Type hints:** Use type annotations where practical, especially for public APIs
- **Naming:** snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Error handling:** Specific exceptions preferred; bare except allowed but discouraged
- **Documentation:** Use docstrings with triple quotes for modules and classes
- **File structure:** Keep modules focused; use tech/ subpackage for utilities
- **Testing:** Place tests in test_*.py files; use pytest fixtures in conftest.py

## Python Compatibility
- **Supported versions:** Python 3.10, 3.11, 3.12, 3.13
- **Type hints:** Currently uses pre-3.10 style (typing.Dict, typing.List) for broader compatibility
- **No deprecated features:** Clean of removed modules (distutils, imp, asyncore)
- **Testing:** Tox tests against py310, py311, py312, py313