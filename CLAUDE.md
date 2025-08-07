# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BEAD is a tool for freezing and storing computations, capturing discrete computations of the form `output = function(*inputs)`. A BEAD captures all three parts: output data files, source code files, and input references to other BEADs. This creates a traceable computation graph for data analysis workflows.

## Architecture

The codebase is split into two main packages:

- **`bead/`** - Core library containing the BEAD format implementation
  - `bead.py` - Core Bead interface and UnpackableBead abstract base class
  - `box.py` - Storage management for beads
  - `workspace.py` - Working directory management  
  - `archive.py` and `ziparchive.py` - Archival format implementations
  - `meta.py` - Metadata definitions (BeadName, InputSpec)
  - `tech/` - Low-level utilities (fs, persistence, timestamps, hashing)

- **`bead_cli/`** - Command-line interface and high-level operations
  - `main.py` - CLI entry point with command parsing
  - `workspace.py` - Workspace command implementations
  - `input.py` - Input management commands
  - `box.py` - Box (storage) management commands  
  - `web/` - Web visualization and graph rendering functionality

## Development Commands

### Testing
```bash
# Run all tests across Python versions
make test
# OR manually with tox
tox

# Run tests with coverage for current Python version
pytest --cov=. --cov-report=term-missing

# Run specific test
pytest path/to/test_file.py::test_function
```

### Linting
```bash
# Lint code (included in tox run)
flake8 bead bead_cli tests
```

### Type Checking
The project uses mypy and pytype for type checking:
```bash
# Type checking is available in dev dependencies
mypy bead bead_cli
pytype bead bead_cli
```

### Building Executables
```bash
# Create platform-specific executables
make executables
# OR manually
dev/build.py
```

This creates self-contained executables in `executables/`:
- `bead` (Unix/Mac)
- `bead.cmd` (Windows) 
- `bead.shiv` (alternative via shiv)

## Key Implementation Patterns

- **Bead Interface**: All bead types implement the `Bead` interface with properties for kind, name, inputs, content_id, freeze_time_str, and box_name
- **UnpackableBead**: Extends Bead with methods to unpack content to workspaces
- **Tech Layer**: Low-level utilities in `bead/tech/` handle filesystem operations, persistence, timestamps, and secure hashing
- **Command Pattern**: CLI commands are organized as classes in the `bead_cli` package with standardized argument parsing
- **Web Visualization**: The `bead_cli/web/` package provides graph visualization capabilities using Graphviz

## Configuration Files

- `pyproject.toml` - Project metadata and build configuration
- `pytest.ini` - Test configuration with test paths and warning filters  
- `tox.ini` - Multi-version testing configuration with flake8 settings
- `Makefile` - Build automation for executables and testing

## Notes

- Requires Python 3.10+
- Tests are located alongside source code in the same directories
- Uses ZIP format for bead archives
- Git integration for version tracking during builds
- Flake8 configured to ignore specific style rules (W503, W504, E251, E241, E221, E722)