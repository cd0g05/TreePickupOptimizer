"""Tests for MST calculator module."""

import pytest
from tree_pickup.mst import calculate_mst_distance
from tree_pickup.models import Address, Coordinate


def test_mst_single_address():
    """Test MST distance with single address."""
    addresses = [
        Address(
            address_string="123 Main St",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=1,
        )
    ]

    distance = calculate_mst_distance(addresses)

    assert distance == 0.0


def test_mst_two_addresses():
    """Test MST distance with two addresses."""
    addresses = [
        Address(
            address_string="123 Main St",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=1,
        ),
        Address(
            address_string="456 Elm St",
            coordinate=Coordinate(latitude=47.6, longitude=-122.1),
            address_number=2,
        ),
    ]

    distance = calculate_mst_distance(addresses)

    assert distance > 0
    assert 10.0 < distance < 20.0


def test_mst_three_addresses_collinear():
    """Test MST with three collinear addresses."""
    addresses = [
        Address(
            address_string="Point A",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=1,
        ),
        Address(
            address_string="Point B",
            coordinate=Coordinate(latitude=47.6, longitude=-122.0),
            address_number=2,
        ),
        Address(
            address_string="Point C",
            coordinate=Coordinate(latitude=47.7, longitude=-122.0),
            address_number=3,
        ),
    ]

    distance = calculate_mst_distance(addresses)

    assert distance > 0


def test_mst_five_addresses(sample_address_objects):
    """Test MST with five addresses."""
    distance = calculate_mst_distance(sample_address_objects)

    assert distance > 0
    assert distance < 100


def test_mst_same_location():
    """Test MST with addresses at same location."""
    addresses = [
        Address(
            address_string="Same 1",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=1,
        ),
        Address(
            address_string="Same 2",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=2,
        ),
        Address(
            address_string="Same 3",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=3,
        ),
    ]

    distance = calculate_mst_distance(addresses)

    assert distance == 0.0
