"""Data validation and outlier detection."""

import sys

from tree_pickup.distance import haversine_distance
from tree_pickup.models import Address


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
        print("[ERROR] Number of teams must be at least 1")
        sys.exit(1)

    if num_teams > num_addresses:
        print(
            f"[ERROR] Cannot create {num_teams} teams with only {num_addresses} addresses. "
            "Reduce team count or add more addresses."
        )
        sys.exit(1)
