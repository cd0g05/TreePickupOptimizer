"""Minimum Spanning Tree distance calculation."""

import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree

from tree_pickup.distance import haversine_distance
from tree_pickup.models import Address


def calculate_mst_distance(addresses: list[Address]) -> float:
    """
    Calculate total MST distance for a set of addresses.

    Args:
        addresses: List of addresses with coordinates

    Returns:
        Total MST distance in kilometers

    Raises:
        ValueError: If any address is missing coordinates
    """
    if len(addresses) <= 1:
        return 0.0

    for addr in addresses:
        if addr.coordinate is None:
            raise ValueError(
                f"Address #{addr.address_number} '{addr.address_string}' "
                "is missing coordinates. All addresses must be geocoded before MST calculation."
            )

    if len(addresses) == 2:
        return haversine_distance(addresses[0].coordinate, addresses[1].coordinate)

    n = len(addresses)
    distance_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            dist = haversine_distance(addresses[i].coordinate, addresses[j].coordinate)
            distance_matrix[i, j] = dist
            distance_matrix[j, i] = dist

    mst = minimum_spanning_tree(distance_matrix)

    total_distance = mst.sum()

    return float(total_distance)
