"""Pytest fixtures for testing."""

import pytest
from unittest.mock import Mock

from tree_pickup.models import Address, Coordinate


@pytest.fixture
def sample_addresses():
    """Sample address strings for testing."""
    return [
        "422 Timber Creek Dr NW, Issaquah, WA 98027",
        "450 Everwood Ct, Issaquah, WA 98027",
        "123 Main St, Bellevue, WA 98004",
        "456 Elm St, Bellevue, WA 98004",
        "789 Oak Ave, Seattle, WA 98101",
    ]


@pytest.fixture
def sample_coordinates():
    """Sample coordinates for testing."""
    return [
        Coordinate(latitude=47.5400, longitude=-122.0326),
        Coordinate(latitude=47.5410, longitude=-122.0330),
        Coordinate(latitude=47.6062, longitude=-122.2000),
        Coordinate(latitude=47.6070, longitude=-122.2010),
        Coordinate(latitude=47.6097, longitude=-122.3331),
    ]


@pytest.fixture
def sample_address_objects(sample_addresses, sample_coordinates):
    """Sample Address objects with coordinates."""
    return [
        Address(address_string=addr, coordinate=coord, address_number=i + 1)
        for i, (addr, coord) in enumerate(zip(sample_addresses, sample_coordinates))
    ]


@pytest.fixture
def duplicate_addresses():
    """Address list with duplicates for testing."""
    return [
        "422 Timber Creek Dr NW, Issaquah, WA 98027",
        "450 Everwood Ct, Issaquah, WA 98027",
        "422 Timber Creek Dr NW, Issaquah, WA 98027",
    ]


@pytest.fixture
def zero_variance_coordinates():
    """Coordinates all at same location."""
    return [
        Coordinate(latitude=47.5400, longitude=-122.0326),
        Coordinate(latitude=47.5400, longitude=-122.0326),
        Coordinate(latitude=47.5400, longitude=-122.0326),
    ]


@pytest.fixture
def mock_nominatim_location():
    """Mock geopy location response."""
    mock_location = Mock()
    mock_location.latitude = 47.5400
    mock_location.longitude = -122.0326
    mock_location.address = "422 Timber Creek Dr NW, Issaquah, WA 98027, USA"
    return mock_location
