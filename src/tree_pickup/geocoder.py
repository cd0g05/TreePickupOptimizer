"""Geocoding with Nominatim API and local caching."""

import certifi
import json
import ssl
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
        # Create SSL context with certifi certificates to avoid SSL verification errors
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.client = Nominatim(user_agent=user_agent, ssl_context=ssl_context)

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
        failed_addresses: list[tuple[int, str, str]] = []

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
                            failed_addresses.append(
                                (idx, original_address, "could not be geocoded")
                            )
                        else:
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
                        failed_addresses.append((idx, original_address, str(e)))
                        progress.update(
                            task, advance=1, description=f"Geocoding addresses ({cache_hits}/{len(addresses)})"
                        )

                        if loop_idx < len(addresses_to_geocode) - 1:
                            time.sleep(1)

        self._save_cache(cache, cache_file)

        success_count = len(addresses) - len(failed_addresses)
        console.print(f"[green]✓[/green] Geocoded {success_count}/{len(addresses)} addresses\n")

        if failed_addresses:
            console.print("[red][ERROR] The following addresses could not be geocoded:[/red]")
            for idx, address, error in failed_addresses:
                console.print(f"[red]  - Address #{idx}: '{address}' - {error}[/red]")
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
