# Tree Pickup Assignment Optimizer

Zero-cost Christmas tree pickup assignment using K-Means clustering and free geocoding. No API keys required!

## Overview

Automatically assign volunteer teams to collect Christmas trees from residential addresses using geographic clustering. The tool groups addresses into compact geographic clusters to minimize travel distance.

## Key Features

- **100% Free**: Uses OpenStreetMap Nominatim geocoding (no API key, no cost)
- **Local Caching**: First run geocodes addresses, subsequent runs are instant
- **Geographic Clustering**: K-Means algorithm creates compact geographic teams
- **Distance Estimation**: MST-based rough distance estimates for route planning
- **Data Quality Warnings**: Detects outliers and data quality issues
- **User-Friendly Errors**: Clear, actionable error messages
- **Reproducible**: Seed-based clustering for consistent results

## Quick Start

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Prepare Your Data

Create `addresses.csv`:

```csv
address
"422 Timber Creek Dr NW, Issaquah, WA 98027"
"450 Everwood Ct, Issaquah, WA 98027"
"123 Main St, Bellevue, WA 98004"
"456 Elm St, Bellevue, WA 98004"
```

### Run

```bash
tree-pickup --addresses addresses.csv --teams 2
```

### Example Output

```
Tree Pickup Assignment Optimizer

✓ Loaded 4 addresses from CSV
✓ Geocoded 4 addresses

Team Assignments:

Team Name    Addresses                                       Rough Estimated Distance
Team Alpha   • 422 Timber Creek Dr NW, Issaquah, WA             1.23 km
             • 450 Everwood Ct, Issaquah, WA
Team Bravo   • 123 Main St, Bellevue, WA                        0.85 km
             • 456 Elm St, Bellevue, WA

✓ Assignment complete!
```

## What Makes This Different?

- **No API Keys**: Most geocoding tools require paid API keys. This uses free OpenStreetMap data.
- **Smart Caching**: Addresses are geocoded once and cached locally. Subsequent runs are instant.
- **Distance Awareness**: Uses Minimum Spanning Tree to estimate total travel distance per team.
- **Quality Warnings**: Automatically detects when teams have addresses >10 miles apart or very high distances.

## How It Works

1. **Parse CSV**: Load and validate addresses from your CSV file
2. **Geocode**: Convert addresses to lat/lng coordinates using Nominatim (cached locally)
3. **Cluster**: Group addresses into K teams using K-Means algorithm
4. **Calculate Distances**: Estimate total travel distance per team using MST
5. **Detect Issues**: Check for outliers and data quality problems
6. **Display**: Show results in formatted table with warnings

## Understanding "Rough Estimated Distance"

The distance shown is a **lower-bound estimate** calculated using Minimum Spanning Tree (MST):

- Uses crow-flies distance (not driving distance)
- Represents minimum possible distance to connect all addresses
- Real travel will be higher due to roads, routing, and return trips
- **Use for comparison** between teams, not actual route planning

## Command Line Options

```bash
tree-pickup --addresses FILE --teams N [--seed SEED] [--cache-file PATH]
```

Options:
- `--addresses FILE` or `-a FILE`: Path to CSV file with addresses (required)
- `--teams N` or `-t N`: Number of teams to create (required)
- `--seed N` or `-s N`: Random seed for reproducibility (default: 42)
- `--cache-file PATH` or `-c PATH`: Cache file location (default: `.geocode_cache.json`)

## Performance

- **First run**: ~1 second per address (Nominatim rate limit)
- **Subsequent runs**: <1 second total (cache hits)
- **Clustering**: Instant even for 100+ addresses

Example: 50 addresses
- First run: ~50 seconds
- Subsequent runs: <1 second

## Documentation

- [SETUP.md](docs/SETUP.md) - Detailed installation instructions
- [USER_GUIDE.md](docs/USER_GUIDE.md) - Complete usage guide with examples
- [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Architecture and development guide

## Requirements

- Python 3.9+
- Internet connection (for first-run geocoding only)

## Dependencies

Core:
- pydantic - Data validation
- rich - Terminal UI
- scikit-learn - K-Means clustering
- geopy - Nominatim geocoding
- scipy - MST algorithm

Development:
- pytest - Testing framework
- pytest-cov - Coverage reporting
- ruff - Linting and formatting

## Testing

Run tests with coverage:

```bash
pip install -e ".[dev]"
pytest --cov=src/tree_pickup --cov-report=term-missing
```

Current coverage: **93%**

## Limitations

This tool does NOT provide:
- Route sequencing (just clustering, not routing order)
- Real driving time/distance calculations
- Individual volunteer tracking
- Hard constraints on team size (K-Means produces unequal clusters)
- Multi-day scheduling
- Depot/starting location optimization

For detailed route planning, use dedicated routing software after getting team assignments.

## Example Use Cases

- Christmas tree pickup by volunteer teams
- Neighborhood canvassing assignments
- Food/package delivery route planning
- Event flyer distribution
- Door-to-door campaigns
- Service area clustering

## FAQ

**Q: Why is first run slow?**
A: Nominatim (free geocoding) rate limits to 1 request/second. Results are cached, so subsequent runs are instant.

**Q: Do I need an API key?**
A: No! Uses free OpenStreetMap Nominatim geocoding.

**Q: Can I change team assignments?**
A: Yes, use different `--seed` values to get different cluster assignments.

**Q: What if addresses are far apart?**
A: You'll get a warning if addresses in same team are >10 miles apart or if total MST distance exceeds 50 miles.

**Q: How accurate is the distance?**
A: It's a lower-bound estimate using crow-flies distance. Real driving distance will be higher. Use for relative comparison, not exact planning.

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for guidelines.

## Support

For issues or questions, please open an issue on the repository.
