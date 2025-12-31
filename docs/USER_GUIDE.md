# User Guide

## Overview

Tree Pickup Assignment Optimizer helps you assign volunteer teams to collect Christmas trees from residential addresses using geographic clustering. The tool automatically groups addresses into compact geographic clusters to minimize travel distance.

## Quick Start

Basic usage:

```bash
tree-pickup --addresses addresses.csv --teams 3
```

This will:
1. Load addresses from your CSV file
2. Geocode them to lat/lng coordinates (cached locally for future runs)
3. Cluster addresses into 3 geographically compact teams
4. Display team assignments with estimated travel distances

## Command Line Options

### Required Arguments

- `--addresses FILE` or `-a FILE`: Path to CSV file containing addresses

- `--teams N` or `-t N`: Number of teams to create

### Optional Arguments

- `--seed N` or `-s N`: Random seed for reproducible clustering (default: 42)

- `--cache-file PATH` or `-c PATH`: Path to geocoding cache file (default: `.geocode_cache.json`)

## CSV File Format

Your CSV file must have a single column named `address` with one address per row:

```csv
address
"422 Timber Creek Dr NW, Issaquah, WA 98027"
"450 Everwood Ct, Issaquah, WA 98027"
"123 Main St, Bellevue, WA 98004"
```

Requirements:
- Header row with column name "address" is required
- Full addresses recommended (street, city, state, zip) for best geocoding accuracy
- No duplicate addresses allowed
- At least one address required

## Understanding the Output

### Team Assignments Table

The tool displays a table with:
- **Team Name**: Auto-generated NATO phonetic alphabet names (Team Alpha, Team Bravo, etc.)
- **Addresses**: List of addresses assigned to this team
- **Rough Estimated Distance**: MST-based distance estimate in kilometers

Example output:

```
Team Assignments:

Team Name       Addresses                                    Rough Estimated Distance
Team Alpha      • 422 Timber Creek Dr NW, Issaquah, WA          5.23 km
                • 450 Everwood Ct, Issaquah, WA
Team Bravo      • 123 Main St, Bellevue, WA                     12.45 km
                • 456 Elm St, Bellevue, WA
                • 789 Oak Ave, Seattle, WA
```

### What is "Rough Estimated Distance"?

The distance shown is calculated using Minimum Spanning Tree (MST) algorithm and represents a **lower bound** on actual travel distance:

- Uses crow-flies distance (Haversine formula), not driving distance
- Connects all addresses in a cluster with minimum total edge length
- Real travel will be higher due to:
  - Road routing (can't travel in straight lines)
  - Return trips to depot or starting points
  - Traffic and road conditions

Think of it as a **comparative metric** - useful for identifying very large routes or unbalanced team assignments, not for actual route planning.

### Warnings

The tool displays warnings for potential data quality issues:

- **Outlier Warning**: "Team Alpha has addresses more than 10 miles apart"
  - Indicates addresses in the same team are geographically distant
  - May indicate data quality issues or very large service area

- **High Distance Warning**: "Team Bravo estimated distance is 52.34 km - verify addresses are correct"
  - Appears when MST distance exceeds 50 miles (80 km)
  - Suggests reviewing addresses for errors

## Geocoding Cache

### How It Works

On first run, addresses are geocoded using Nominatim (OpenStreetMap) API:
- Rate limited to 1 request/second (respectful usage policy)
- Results saved to `.geocode_cache.json` in your working directory
- Subsequent runs load from cache instantly (no API calls)

### Benefits

- **Free**: No API key needed, no cost
- **Fast subsequent runs**: Instant loading from cache
- **Offline after first run**: No internet needed for cached addresses

### Cache Management

The cache file stores:
```json
{
  "123 main st": {
    "lat": 47.5,
    "lng": -122.0,
    "display_name": "123 Main St, City, State, ZIP, Country"
  }
}
```

To refresh geocoding (if addresses have changed):
```bash
rm .geocode_cache.json
```

## Error Messages

### Common Errors and Solutions

**File not found**
```
[ERROR] File not found: addresses.csv
```
Solution: Check the file path is correct and file exists

**CSV missing 'address' column**
```
[ERROR] CSV missing 'address' column. Ensure your CSV has a header row with an 'address' column.
```
Solution: Add header row with "address" as the column name

**No addresses in CSV**
```
[ERROR] CSV contains no addresses. Add addresses to your CSV file.
```
Solution: Add at least one address to your CSV file

**Duplicate address found**
```
[ERROR] Duplicate address found: '123 Main St'. Remove duplicates and try again.
```
Solution: Remove duplicate entries from your CSV

**Too many teams**
```
[ERROR] Cannot create 10 teams with only 5 addresses. Reduce team count or add more addresses.
```
Solution: Reduce the number of teams or add more addresses to your CSV

**Geocoding failed**
```
[ERROR] Invalid address: Address #5 '123 Fake St' could not be geocoded. Check your addresses and verify them.
```
Solution: Review address for typos, ensure it's a real location, use full address format

## Advanced Usage

### Reproducible Clustering

For consistent results across multiple runs:

```bash
tree-pickup --addresses addresses.csv --teams 3 --seed 42
```

Same seed always produces same cluster assignments.

### Different Clustering

To try different team assignments:

```bash
tree-pickup --addresses addresses.csv --teams 3 --seed 100
```

Different seeds produce different cluster assignments.

### Custom Cache Location

To use a different cache file:

```bash
tree-pickup --addresses addresses.csv --teams 3 --cache-file /path/to/cache.json
```

Useful for multiple projects or testing.

## Tips for Best Results

1. **Use Full Addresses**: Include street, city, state, and ZIP for best geocoding accuracy
   - Good: "123 Main St, Seattle, WA 98101"
   - Poor: "123 Main St"

2. **Verify Data Quality**: Check for duplicate addresses or typos before running

3. **Right-Size Teams**: Consider your service area size when choosing team count
   - Too many teams: Each gets very few addresses
   - Too few teams: Large geographic areas per team

4. **Review Warnings**: Pay attention to outlier and high distance warnings

5. **Test Different Seeds**: Try a few different seeds to find best geographic clustering

## Limitations

What this tool does NOT do:

- Route sequencing (just clustering, not routing order)
- Real driving time/distance calculations
- Individual volunteer tracking within teams
- Hard constraints on team size (cluster sizes may vary)
- Multi-day scheduling
- Depot/starting location optimization

For detailed route planning, export addresses and use dedicated routing software like Google Maps or route optimization tools.
