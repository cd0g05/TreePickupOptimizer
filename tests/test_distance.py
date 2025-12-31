"""Tests for distance calculator module."""

import pytest
from tree_pickup.distance import haversine_distance
from tree_pickup.models import Coordinate


def test_haversine_same_coordinates():
    """Test distance between identical coordinates is zero."""
    coord = Coordinate(latitude=47.5, longitude=-122.0)

    distance = haversine_distance(coord, coord)

    assert distance == 0.0


def test_haversine_known_distance():
    """Test Haversine calculation with known coordinates."""
    seattle = Coordinate(latitude=47.6062, longitude=-122.3321)
    bellevue = Coordinate(latitude=47.6101, longitude=-122.2015)

    distance = haversine_distance(seattle, bellevue)

    assert 9.0 < distance < 11.0


@pytest.mark.parametrize(
    "lat1,lon1,lat2,lon2,expected_min,expected_max",
    [
        (47.5, -122.0, 47.5, -122.1, 7.0, 9.0),
        (47.5, -122.0, 47.6, -122.0, 10.0, 12.0),
        (0, 0, 0, 1, 110.0, 112.0),
        (0, 0, 1, 0, 110.0, 112.0),
    ],
)
def test_haversine_parametrized(lat1, lon1, lat2, lon2, expected_min, expected_max):
    """Test Haversine with various coordinate pairs."""
    coord1 = Coordinate(latitude=lat1, longitude=lon1)
    coord2 = Coordinate(latitude=lat2, longitude=lon2)

    distance = haversine_distance(coord1, coord2)

    assert expected_min < distance < expected_max


def test_haversine_symmetry():
    """Test that distance A->B equals distance B->A."""
    coord1 = Coordinate(latitude=47.5, longitude=-122.0)
    coord2 = Coordinate(latitude=47.6, longitude=-122.1)

    distance_ab = haversine_distance(coord1, coord2)
    distance_ba = haversine_distance(coord2, coord1)

    assert abs(distance_ab - distance_ba) < 0.001


def test_haversine_positive():
    """Test that distances are always positive."""
    coord1 = Coordinate(latitude=47.5, longitude=-122.0)
    coord2 = Coordinate(latitude=-47.5, longitude=122.0)

    distance = haversine_distance(coord1, coord2)

    assert distance > 0
