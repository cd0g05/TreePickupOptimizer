"""Tests for geocoder module."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, call
from tree_pickup.geocoder import Geocoder
from tree_pickup.models import Coordinate


def test_geocode_with_cache_hits(tmp_path):
    """Test geocoding when all addresses are in cache."""
    cache_file = tmp_path / "cache.json"
    cache_data = {
        "123 main st": {"lat": 47.5, "lng": -122.0, "display_name": "123 Main St, City, WA"},
        "456 elm st": {"lat": 47.6, "lng": -122.1, "display_name": "456 Elm St, City, WA"},
    }
    cache_file.write_text(json.dumps(cache_data))

    geocoder = Geocoder()
    addresses = ["123 Main St", "456 Elm St"]

    coords = geocoder.geocode_addresses(addresses, str(cache_file))

    assert len(coords) == 2
    assert coords[0] == Coordinate(latitude=47.5, longitude=-122.0)
    assert coords[1] == Coordinate(latitude=47.6, longitude=-122.1)


@patch("tree_pickup.geocoder.Nominatim")
@patch("time.sleep")
def test_geocode_with_cache_misses(mock_sleep, mock_nominatim_class, tmp_path, mock_nominatim_location):
    """Test geocoding with API calls for cache misses."""
    cache_file = tmp_path / "cache.json"
    cache_file.write_text("{}")

    mock_client = Mock()
    mock_nominatim_class.return_value = mock_client
    mock_client.geocode.return_value = mock_nominatim_location

    geocoder = Geocoder()
    addresses = ["123 Main St"]

    coords = geocoder.geocode_addresses(addresses, str(cache_file))

    assert len(coords) == 1
    assert coords[0] == Coordinate(latitude=47.5400, longitude=-122.0326)

    mock_client.geocode.assert_called_once_with("123 Main St", timeout=10)

    with open(cache_file, "r") as f:
        saved_cache = json.load(f)

    assert "123 main st" in saved_cache
    assert saved_cache["123 main st"]["lat"] == 47.5400


@patch("tree_pickup.geocoder.Nominatim")
def test_geocode_failure(mock_nominatim_class, tmp_path):
    """Test error handling when geocoding fails."""
    cache_file = tmp_path / "cache.json"
    cache_file.write_text("{}")

    mock_client = Mock()
    mock_nominatim_class.return_value = mock_client
    mock_client.geocode.return_value = None

    geocoder = Geocoder()
    addresses = ["Invalid Address"]

    with pytest.raises(SystemExit) as exc_info:
        geocoder.geocode_addresses(addresses, str(cache_file))

    assert exc_info.value.code == 1


@patch("tree_pickup.geocoder.Nominatim")
@patch("time.sleep")
def test_rate_limiting(mock_sleep, mock_nominatim_class, tmp_path, mock_nominatim_location):
    """Test that rate limiting sleeps between requests."""
    cache_file = tmp_path / "cache.json"
    cache_file.write_text("{}")

    mock_client = Mock()
    mock_nominatim_class.return_value = mock_client
    mock_client.geocode.return_value = mock_nominatim_location

    geocoder = Geocoder()
    addresses = ["123 Main St", "456 Elm St"]

    coords = geocoder.geocode_addresses(addresses, str(cache_file))

    assert len(coords) == 2
    mock_sleep.assert_called_once_with(1)


def test_load_nonexistent_cache(tmp_path):
    """Test loading cache when file doesn't exist."""
    geocoder = Geocoder()
    cache_file = tmp_path / "nonexistent.json"

    cache = geocoder._load_cache(str(cache_file))

    assert cache == {}


def test_load_corrupted_cache(tmp_path):
    """Test loading cache with corrupted JSON."""
    cache_file = tmp_path / "corrupted.json"
    cache_file.write_text("not valid json {")

    geocoder = Geocoder()
    cache = geocoder._load_cache(str(cache_file))

    assert cache == {}


@patch("tree_pickup.geocoder.Nominatim")
def test_user_agent_set(mock_nominatim_class):
    """Test that User-Agent is set correctly."""
    geocoder = Geocoder()

    mock_nominatim_class.assert_called_once_with(user_agent="tree-pickup-optimizer")
