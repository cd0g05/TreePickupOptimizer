# Development Guide

## Architecture Overview

This project uses a professional package structure with clear separation of concerns:

```
tree-pickup/
├── src/tree_pickup/          # Main package
│   ├── __init__.py            # Package initialization
│   ├── cli.py                 # CLI entry point
│   ├── models.py              # Pydantic data models
│   ├── csv_parser.py          # CSV parsing and validation
│   ├── geocoder.py            # Nominatim geocoding with caching
│   ├── distance.py            # Haversine distance calculation
│   ├── mst.py                 # Minimum Spanning Tree algorithm
│   ├── clusterer.py           # K-Means clustering engine
│   ├── team_generator.py      # NATO phonetic team names
│   └── validators.py          # Data validation and outlier detection
├── tests/                     # Test suite (pytest)
└── docs/                      # Documentation
```

## Data Flow

```
CSV File
  ↓
CSV Parser (validation, duplicate detection)
  ↓
Geocoder (Nominatim API + local cache)
  ↓
Address Objects (with coordinates)
  ↓
K-Means Clusterer (geographic grouping)
  ↓
MST Calculator (distance estimation per team)
  ↓
Validators (outlier detection, warnings)
  ↓
CLI Output (Rich table + warnings)
```

## Core Components

### 1. Data Models (`models.py`)

Uses Pydantic for validation:

- `Coordinate`: Lat/lng with range validation
- `Address`: Address string + coordinate + number (for error messages)
- `Team`: Name + addresses + MST distance + warnings
- `ClusterResult`: Complete result with all teams and global warnings

### 2. CSV Parser (`csv_parser.py`)

Responsibilities:
- Read CSV with single "address" column
- Validate file format (header, columns, data)
- Detect duplicates using normalized addresses
- Graceful error handling with actionable messages

Normalization: lowercase, strip whitespace, collapse multiple spaces

### 3. Geocoder (`geocoder.py`)

Responsibilities:
- Geocode addresses using Nominatim (OpenStreetMap)
- Local file-based caching (`.geocode_cache.json`)
- Rate limiting (1 req/sec per Nominatim policy)
- Rich progress bar for long operations
- Error handling with address numbers for debugging

Cache format:
```json
{
  "normalized_address": {
    "lat": 47.5,
    "lng": -122.0,
    "display_name": "Full geocoded address"
  }
}
```

### 4. Distance Calculator (`distance.py`)

Haversine formula implementation:
- Great-circle distance on Earth's surface
- Returns distance in kilometers
- Pure math function (no API calls)

Formula constants:
- Earth radius: 6371 km
- Converts lat/lng to radians
- Uses sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)

### 5. MST Calculator (`mst.py`)

Minimum Spanning Tree for distance estimation:
- Builds full distance matrix using Haversine
- Uses scipy.sparse.csgraph.minimum_spanning_tree
- Returns sum of MST edge weights

Purpose: Rough lower-bound estimate of total travel distance

### 6. Validators (`validators.py`)

Two validation functions:

**Outlier Detection:**
- Check pairwise distances within cluster
- Default threshold: 16 km (10 miles)
- Returns warnings if any pair exceeds threshold

**Team Count Validation:**
- Ensure num_teams >= 1
- Ensure num_teams <= num_addresses
- Exit with clear error message if invalid

### 7. Clusterer (`clusterer.py`)

K-Means clustering implementation:
- Uses scikit-learn KMeans
- Configurable random seed for reproducibility
- n_init=10 for stable results
- Assigns team names from generator
- Calculates MST distance per team
- Detects outliers per team
- Adds high-distance warnings (>80 km)

### 8. Team Generator (`team_generator.py`)

NATO phonetic alphabet names:
- First 26 teams: Alpha through Zulu
- 27+: Alpha 2, Bravo 2, etc.
- Deterministic and scalable

### 9. CLI (`cli.py`)

Orchestrates the full workflow:
1. Parse arguments (argparse)
2. Load and validate CSV
3. Validate team count
4. Geocode addresses (with caching)
5. Create Address objects
6. Generate team names
7. Cluster addresses
8. Display Rich table with results
9. Display warnings if any

Uses Rich for:
- Console output with colors
- Progress bars (geocoding only)
- Formatted tables
- Warning messages (yellow)

## Error Handling Philosophy

**Fail fast with clear guidance:**
- Every error includes what went wrong
- Every error includes how to fix it
- Use sys.exit(1) for fatal errors
- Non-fatal issues become warnings (displayed but don't block)

Error message format:
```
[ERROR] {what went wrong}. {how to fix it}.
```

Examples:
- "Duplicate address found: '123 Main St'. Remove duplicates and try again."
- "Cannot create 10 teams with only 5 addresses. Reduce team count or add more addresses."

## Warning System

Non-fatal warnings collected during processing:

**Team-level warnings:**
- Outliers (addresses >10 miles apart)
- High MST distance (>50 miles)

**Display:**
- Warnings shown after results table
- Yellow/orange color for visibility
- Format: "⚠ WARNING: Team Alpha - {specific issue}"

## Testing Strategy

### Framework

- pytest with pytest-cov
- pytest-mock for mocking external dependencies
- Target: 75%+ coverage (currently 93%)

### Test Structure

**Unit tests** for each module:
- CSV parser: Format validation, duplicates, errors
- Geocoder: Caching, API mocking, rate limiting
- Distance: Haversine correctness, edge cases
- MST: Various configurations, single/two/many addresses
- Clusterer: Basic clustering, edge cases, reproducibility
- Validators: Outlier detection, team count validation
- Team generator: Name uniqueness, scaling beyond 26

**Integration tests** for CLI:
- End-to-end workflow with mocked geocoder
- Argument parsing
- Error handling
- Output formatting

### Running Tests

```bash
pytest --cov=src/tree_pickup --cov-report=term-missing --cov-fail-under=75
```

View HTML coverage report:
```bash
pytest --cov=src/tree_pickup --cov-report=html
open htmlcov/index.html
```

### Fixtures

Located in `tests/conftest.py`:
- `sample_addresses` - List of address strings
- `sample_coordinates` - List of Coordinate objects
- `sample_address_objects` - Full Address objects with coords
- `duplicate_addresses` - For duplicate detection testing
- `zero_variance_coordinates` - All same location
- `mock_nominatim_location` - Mocked geopy response

## Code Quality

### Linting and Formatting

Uses Ruff for fast linting and formatting:

```bash
ruff check .
ruff format .
```

Configuration in `pyproject.toml`:
- Line length: 100
- Target: Python 3.9
- Selected rules: E, F, I, N, W (errors, imports, naming, warnings)

### Type Hints

All functions and methods use type hints:
```python
def haversine_distance(coord1: Coordinate, coord2: Coordinate) -> float:
```

Pydantic models provide runtime validation.

### Dependencies

**Production:**
- pydantic>=2.0 - Data validation
- rich>=13.0 - Terminal UI
- scikit-learn>=1.3 - K-Means clustering
- geopy>=2.4 - Nominatim client
- scipy>=1.11 - MST algorithm

**Development:**
- pytest>=7.4 - Testing
- pytest-cov>=4.1 - Coverage
- pytest-mock>=3.12 - Mocking
- ruff>=0.1 - Linting/formatting

## Adding New Features

### Example: Adding Export to JSON

1. **Create new module** (`src/tree_pickup/exporter.py`):
```python
import json
from tree_pickup.models import ClusterResult

def export_to_json(result: ClusterResult, output_file: str) -> None:
    """Export cluster result to JSON file."""
    data = {
        "teams": [
            {
                "name": team.name,
                "addresses": [addr.address_string for addr in team.addresses],
                "distance_km": team.mst_distance_km,
            }
            for team in result.teams
        ]
    }
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
```

2. **Add CLI flag** (in `cli.py`):
```python
parser.add_argument("--export", "-e", help="Export results to JSON file")

# After clustering:
if args.export:
    export_to_json(result, args.export)
    console.print(f"[green]✓ Exported to {args.export}[/green]")
```

3. **Write tests** (`tests/test_exporter.py`):
```python
def test_export_to_json(tmp_path, sample_cluster_result):
    output_file = tmp_path / "output.json"
    export_to_json(sample_cluster_result, str(output_file))

    with open(output_file) as f:
        data = json.load(f)

    assert len(data["teams"]) == 3
```

4. **Run tests and check coverage**

5. **Update documentation** (USER_GUIDE.md, DEVELOPMENT.md)

## Debugging Tips

### Enable verbose geocoding:

Modify `geocoder.py` to print cache hits/misses.

### Test with small dataset:

Use 3-5 addresses for faster iteration during development.

### Inspect clustering:

Print cluster labels after K-Means:
```python
print(f"Cluster labels: {labels}")
```

### Check MST calculation:

Print distance matrix before MST:
```python
print(f"Distance matrix:\n{distance_matrix}")
```

## Performance Considerations

### Geocoding

- First run: ~1 second per address (Nominatim rate limit)
- Subsequent runs: <1 second total (cache hits)
- For 100 addresses: ~100 seconds first run, instant after

### Clustering

- K-Means is fast even for large datasets
- 100 addresses: <1 second
- 1000 addresses: <5 seconds

### MST

- scipy.sparse.csgraph.minimum_spanning_tree is efficient
- 100 addresses: <1 second
- Bottleneck is building distance matrix (O(n²) Haversine calls)

## Contributing Guidelines

1. **Fork and clone** the repository
2. **Create feature branch**: `git checkout -b feature/my-feature`
3. **Make changes** following existing patterns
4. **Write tests** for new functionality
5. **Run tests**: Ensure 75%+ coverage
6. **Run linter**: `ruff check . && ruff format .`
7. **Update docs** if adding user-facing features
8. **Commit** with clear message
9. **Push and create PR**

## Future Enhancement Ideas

- Constrained K-Means (max cluster size)
- Alternative geocoding providers (Google, HERE)
- CSV/JSON export for route planning tools
- Cache expiration mechanism
- Map visualization (folium)
- Driving distance via OSRM
- Multi-depot optimization
- Load balancing constraints
