"""Tests for validators module."""

import pytest
from tree_pickup.validators import detect_outliers, validate_capacity, validate_team_count
from tree_pickup.models import Address, Coordinate


def test_detect_outliers_none():
    """Test outlier detection with no outliers."""
    addresses = [
        Address(
            address_string="Close 1",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=1,
        ),
        Address(
            address_string="Close 2",
            coordinate=Coordinate(latitude=47.501, longitude=-122.001),
            address_number=2,
        ),
    ]

    warnings = detect_outliers(addresses)

    assert len(warnings) == 0


def test_detect_outliers_found():
    """Test outlier detection with addresses >10 miles apart."""
    addresses = [
        Address(
            address_string="Far 1",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=1,
        ),
        Address(
            address_string="Far 2",
            coordinate=Coordinate(latitude=47.7, longitude=-122.3),
            address_number=2,
        ),
    ]

    warnings = detect_outliers(addresses)

    assert len(warnings) == 1
    assert "10 miles apart" in warnings[0]


def test_detect_outliers_single_address():
    """Test outlier detection with single address."""
    addresses = [
        Address(
            address_string="Single",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=1,
        )
    ]

    warnings = detect_outliers(addresses)

    assert len(warnings) == 0


def test_detect_outliers_boundary():
    """Test outlier detection at threshold boundary."""
    addresses = [
        Address(
            address_string="Point A",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=1,
        ),
        Address(
            address_string="Point B",
            coordinate=Coordinate(latitude=47.64, longitude=-122.0),
            address_number=2,
        ),
    ]

    warnings_15km = detect_outliers(addresses, threshold_km=15.0)
    warnings_17km = detect_outliers(addresses, threshold_km=17.0)

    assert len(warnings_15km) == 1
    assert len(warnings_17km) == 0


def test_validate_team_count_valid():
    """Test validation with valid team count."""
    validate_team_count(10, 3)
    validate_team_count(10, 10)
    validate_team_count(10, 1)


def test_validate_team_count_too_many():
    """Test validation when team count exceeds addresses."""
    with pytest.raises(SystemExit) as exc_info:
        validate_team_count(5, 10)

    assert exc_info.value.code == 1


def test_validate_team_count_zero():
    """Test validation with zero teams."""
    with pytest.raises(SystemExit) as exc_info:
        validate_team_count(10, 0)

    assert exc_info.value.code == 1


def test_validate_team_count_negative():
    """Test validation with negative teams."""
    with pytest.raises(SystemExit) as exc_info:
        validate_team_count(10, -1)

    assert exc_info.value.code == 1


def test_validate_capacity_exceeds_threshold():
    """Test capacity validation when threshold is exceeded."""
    with pytest.raises(SystemExit) as exc_info:
        validate_capacity(20, 3, 8)

    assert exc_info.value.code == 1


def test_validate_capacity_at_threshold():
    """Test capacity validation just below threshold (should pass)."""
    validate_capacity(19, 3, 8)


def test_validate_capacity_below_threshold():
    """Test capacity validation below threshold (should pass)."""
    validate_capacity(18, 3, 8)
    validate_capacity(10, 3, 8)
    validate_capacity(1, 1, 8)
