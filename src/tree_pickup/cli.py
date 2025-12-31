"""CLI entry point for tree pickup assignment optimizer."""

import argparse
import sys

from rich.console import Console
from rich.table import Table

from tree_pickup.clusterer import Clusterer
from tree_pickup.csv_parser import parse_addresses
from tree_pickup.geocoder import Geocoder
from tree_pickup.models import Address
from tree_pickup.team_generator import generate_team_names
from tree_pickup.validators import validate_team_count

console = Console()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Tree Pickup Assignment Optimizer - Geographic clustering for volunteer teams"
    )

    parser.add_argument(
        "--addresses", "-a", required=True, help="Path to CSV file with addresses"
    )

    parser.add_argument(
        "--teams", "-t", type=int, required=True, help="Number of teams to create"
    )

    parser.add_argument(
        "--seed", "-s", type=int, default=42, help="Random seed for reproducibility (default: 42)"
    )

    parser.add_argument(
        "--cache-file",
        "-c",
        default=".geocode_cache.json",
        help="Path to geocoding cache file (default: .geocode_cache.json)",
    )

    args = parser.parse_args()

    console.print("[bold blue]Tree Pickup Assignment Optimizer[/bold blue]\n")

    address_strings = parse_addresses(args.addresses)
    console.print(f"[green]✓[/green] Loaded {len(address_strings)} addresses from CSV\n")

    validate_team_count(len(address_strings), args.teams)

    geocoder = Geocoder()
    coordinates = geocoder.geocode_addresses(address_strings, args.cache_file)
    console.print(f"[green]✓[/green] Geocoded {len(coordinates)} addresses\n")

    addresses = [
        Address(address_string=addr_str, coordinate=coord, address_number=i + 1)
        for i, (addr_str, coord) in enumerate(zip(address_strings, coordinates))
    ]

    team_names = generate_team_names(args.teams)

    clusterer = Clusterer()
    result = clusterer.cluster_addresses(addresses, args.teams, team_names, args.seed)

    console.print("[bold green]Team Assignments:[/bold green]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Team Name", style="cyan", width=20)
    table.add_column("Addresses", style="white")
    table.add_column("Rough Estimated Distance", style="yellow", justify="right")

    for team in result.teams:
        address_list = "\n".join([f"• {addr.address_string}" for addr in team.addresses])

        distance_str = f"{team.mst_distance_km:.2f} km"

        team_name = team.name
        if team.warnings:
            team_name += " ⚠"

        table.add_row(team_name, address_list, distance_str)

    console.print(table)

    warnings_found = False
    for team in result.teams:
        if team.warnings:
            warnings_found = True
            for warning in team.warnings:
                console.print(f"\n[yellow]⚠ WARNING: {team.name} - {warning}[/yellow]")

    if result.global_warnings:
        warnings_found = True
        for warning in result.global_warnings:
            console.print(f"\n[yellow]⚠ WARNING: {warning}[/yellow]")

    if warnings_found:
        console.print()

    console.print("[bold green]✓ Assignment complete![/bold green]")

    sys.exit(0)


if __name__ == "__main__":
    main()
