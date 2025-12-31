"""Geocoding with Nominatim API and local caching."""

import json
import sys
import time
from pathlib import Path

from geopy.geocoders import Nominatim
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from tree_pickup.csv_parser import normalize_address
from tree_pickup.models import Coordinate

console = Console()


class Geocoder:
    """Geocoder with local file-based caching."""

    def __init__(self, user_agent: str = "tree-pickup-optimizer"):
        """Initialize geocoder with Nominatim client."""
        self.client = Nominatim(user_agent=user_agent)

    def geocode_addresses(
        self, addresses: list[str], cache_file: str = ".geocode_cache.json"
    ) -> list[Coordinate]:
        """
        Geocode addresses with local caching.

        Args:
            addresses: List of address strings to geocode
            cache_file: Path to cache file

        Returns:
            List of Coordinate objects

        Raises:
            SystemExit: If any address fails to geocode
        """
        cache = self._load_cache(cache_file)
        coordinates = []
        cache_hits = 0
        cache_misses = 0

        addresses_to_geocode = []
        for i, address in enumerate(addresses, 1):
            normalized = normalize_address(address)
            if normalized in cache:
                cache_hits += 1
                cached_data = cache[normalized]
                coordinates.append(
                    Coordinate(latitude=cached_data["lat"], longitude=cached_data["lng"])
                )
            else:
                cache_misses += 1
                addresses_to_geocode.append((i, address, normalized))

        if cache_misses > 0:
            if cache_misses > 30:
                console.print(
                    f"[yellow]Geocoding {cache_misses} addresses will take "
                    f"approximately {cache_misses} seconds...[/yellow]"
                )

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Geocoding addresses ({cache_hits}/{len(addresses)})", total=cache_misses
                )

                for loop_idx, (idx, original_address, normalized) in enumerate(addresses_to_geocode):
                    try:
                        location = self.client.geocode(original_address, timeout=10)

                        if location is None:
                            console.print(
                                f"\n[red][ERROR] Invalid address: Address #{idx} "
                                f"'{original_address}' could not be geocoded. "
                                f"Check your addresses and verify them.[/red]"
                            )
                            sys.exit(1)

                        coord = Coordinate(latitude=location.latitude, longitude=location.longitude)
                        coordinates.append(coord)

                        cache[normalized] = {
                            "lat": location.latitude,
                            "lng": location.longitude,
                            "display_name": location.address,
                        }

                        cache_hits += 1
                        progress.update(
                            task, advance=1, description=f"Geocoding addresses ({cache_hits}/{len(addresses)})"
                        )

                        if loop_idx < len(addresses_to_geocode) - 1:
                            time.sleep(1)

                    except Exception as e:
                        console.print(
                            f"\n[red][ERROR] Failed to geocode address #{idx} "
                            f"'{original_address}': {e}[/red]"
                        )
                        sys.exit(1)

        self._save_cache(cache, cache_file)

        if len(coordinates) != len(addresses):
            console.print(
                f"[red][ERROR] Geocoding incomplete: Expected {len(addresses)} coordinates "
                f"but got {len(coordinates)}. Some addresses failed to geocode.[/red]"
            )
            sys.exit(1)

        return coordinates

    def _load_cache(self, cache_file: str) -> dict:
        """Load geocoding cache from file."""
        path = Path(cache_file)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Geocoding cache file '{cache_file}' is corrupted and will be "
                    f"rebuilt. Error: {e}[/yellow]"
                )
                return {}
        return {}

    def _save_cache(self, cache: dict, cache_file: str) -> None:
        """Save geocoding cache to file."""
        path = Path(cache_file)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to save cache: {e}[/yellow]")
