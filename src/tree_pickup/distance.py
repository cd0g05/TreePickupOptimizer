"""Distance calculations using Haversine formula."""

import math

from tree_pickup.models import Coordinate


def haversine_distance(coord1: Coordinate, coord2: Coordinate) -> float:
    """
    Calculate great-circle distance between two coordinates.

    Uses the Haversine formula to calculate distance on Earth's surface.

    Args:
        coord1: First coordinate
        coord2: Second coordinate

    Returns:
        Distance in kilometers
    """
    if coord1.latitude == coord2.latitude and coord1.longitude == coord2.longitude:
        return 0.0

    R = 6371

    lat1_rad = math.radians(coord1.latitude)
    lat2_rad = math.radians(coord2.latitude)
    delta_lat = math.radians(coord2.latitude - coord1.latitude)
    delta_lon = math.radians(coord2.longitude - coord1.longitude)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(
        delta_lon / 2
    ) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c

    return distance
