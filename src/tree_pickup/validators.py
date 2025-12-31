"""Data validation and outlier detection."""

import sys

from rich.console import Console

from tree_pickup.distance import haversine_distance
from tree_pickup.models import Address

console = Console()


def detect_outliers(addresses: list[Address], threshold_km: float = 16.0) -> list[str]:
    """
    Detect outlier addresses within a cluster.

    Args:
        addresses: List of addresses to check
        threshold_km: Distance threshold in km (default 16.0 km = ~10 miles)

    Returns:
        List of warning messages
    """
    warnings = []

    if len(addresses) <= 1:
        return warnings

    for i in range(len(addresses)):
        for j in range(i + 1, len(addresses)):
            dist = haversine_distance(addresses[i].coordinate, addresses[j].coordinate)
            if dist > threshold_km:
                warnings.append("Addresses more than 10 miles apart detected")
                return warnings

    return warnings


def validate_team_count(num_addresses: int, num_teams: int) -> None:
    """
    Validate team count is valid for number of addresses.

    Args:
        num_addresses: Number of addresses to cluster
        num_teams: Number of teams to create

    Raises:
        SystemExit: If validation fails
    """
    if num_teams < 1:
        console.print("[red][ERROR] Number of teams must be at least 1[/red]")
        sys.exit(1)

    if num_teams > num_addresses:
        console.print(
            f"[red][ERROR] Cannot create {num_teams} teams with only {num_addresses} addresses. "
            "Reduce team count or add more addresses.[/red]"
        )
        sys.exit(1)


def validate_capacity(num_addresses: int, num_teams: int, max_trees: int) -> None:
    """
    Validate that the number of addresses doesn't exceed safe capacity.

    Args:
        num_addresses: Number of addresses to cluster
        num_teams: Number of teams to create
        max_trees: Maximum addresses per team

    Raises:
        SystemExit: If capacity threshold exceeded
    """
    # Use 80% threshold to provide safety buffer for K-Means clustering variability.
    # K-Means does not guarantee equal cluster sizes, so perfect 100% capacity
    # would risk some teams exceeding max-trees before redistribution can fix it.
    threshold = (num_teams * max_trees) * 0.8

    if num_addresses >= threshold:
        console.print(
            f"[red][ERROR] Capacity exceeded: {num_addresses} addresses with {num_teams} teams "
            f"at {max_trees} max trees per team exceeds safe capacity. "
            f"Increase --max-trees or --teams to proceed.[/red]"
        )
        sys.exit(1)
