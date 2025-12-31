# Setup Guide

## Quick Start

**NO API KEY NEEDED!** This tool uses free OpenStreetMap geocoding (Nominatim) - zero cost, zero signup.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Internet connection (for first-run geocoding only)

## Installation

### 1. Clone or Download the Repository

```bash
cd /path/to/tree-pickup
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

**On Windows:**
```cmd
.venv\Scripts\activate
```

### 4. Install the Package

```bash
pip install -e .
```

This installs:
- Core dependencies: pydantic, rich, scikit-learn, geopy, scipy
- Makes `tree-pickup` command available globally (while venv is activated)

### 5. Verify Installation

```bash
tree-pickup --help
```

You should see help text with available options.

## Prepare Your Address Data

### 1. Create CSV File

Create a file named `addresses.csv` with this format:

```csv
address
"422 Timber Creek Dr NW, Issaquah, WA 98027"
"450 Everwood Ct, Issaquah, WA 98027"
"123 Main St, Bellevue, WA 98004"
"456 Elm St, Bellevue, WA 98004"
```

**Important:**
- First row must be header with "address" column name
- Use full addresses (street, city, state, ZIP) for best results
- No duplicates allowed

### 2. Sample Data

The repository includes `addresses.csv` with sample addresses you can use for testing.

## Run Your First Assignment

```bash
tree-pickup --addresses addresses.csv --teams 2
```

On first run:
- Geocoding will take ~1 second per address (Nominatim rate limit)
- Progress bar shows geocoding status
- Results are cached locally for future runs

Subsequent runs with same addresses are instant (loads from cache).

## What Gets Created

After first run, you'll see:
- `.geocode_cache.json` - Cached geocoding results (gitignored)
- Terminal output with team assignments and distances

## Development Installation

For development (includes test tools):

```bash
pip install -e ".[dev]"
```

This adds:
- pytest - Testing framework
- pytest-cov - Coverage reporting
- pytest-mock - Mocking utilities
- ruff - Linting and formatting

Run tests:

```bash
pytest --cov=src/tree_pickup --cov-report=term-missing
```

## Troubleshooting

### Virtual Environment Not Activating

**Problem:** `tree-pickup: command not found`

**Solution:** Make sure virtual environment is activated (you should see `(.venv)` in your prompt)

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'pydantic'`

**Solution:** Install package with `pip install -e .`

### Geocoding Timeout

**Problem:** Geocoding takes a long time

**Solution:** This is normal for first run - Nominatim rate limit is 1 request/second. Future runs use cache and are instant.

### Permission Errors

**Problem:** Cannot write cache file

**Solution:** Check directory permissions, ensure you have write access to working directory

## Upgrading

If you pull new code:

```bash
source .venv/bin/activate
pip install -e .
```

This reinstalls with any new dependencies.

## Uninstalling

```bash
pip uninstall tree-pickup
```

To remove virtual environment:

```bash
deactivate
rm -rf .venv
```

## Next Steps

- Read [USER_GUIDE.md](USER_GUIDE.md) for detailed usage instructions
- Read [DEVELOPMENT.md](DEVELOPMENT.md) if you want to contribute or modify the code
- Try different seeds to see different clustering results
- Review the warning system for data quality insights
