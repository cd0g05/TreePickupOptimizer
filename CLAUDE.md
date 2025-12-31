# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`tree-pickup` is a Python project managed using `pyproject.toml` with minimal dependencies. The project uses Python 3.9+ and includes a virtual environment setup.

## Development Environment

- **Python Version**: 3.9 (specified in `.python-version`)
- **Virtual Environment**: `.venv` directory (already configured)
- **Package Manager**: Uses standard Python packaging with `pyproject.toml`

## Common Commands

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies (when added to pyproject.toml)
pip install -e .
```

### Running the Application
```bash
# Run the main script
python main.py
```

### Package Management
```bash
# Add a new dependency to pyproject.toml manually, then:
pip install -e .

# Or install a specific package:
pip install <package-name>
```

## Code Structure

Currently minimal structure:
- `main.py`: Entry point with a simple `main()` function
- `pyproject.toml`: Project metadata and dependencies
- `.venv/`: Virtual environment (git-ignored)
- `_bmad/`: BMAD framework files for development workflows (not part of the main application)

## Project-Specific Notes

- The `_bmad/` directory contains BMAD (Build, Manage, Automate, Deploy) framework files used for development workflow automation. These are tooling/infrastructure files and should not be modified as part of regular application development.
- This project is in early stages with minimal functionality currently implemented.
