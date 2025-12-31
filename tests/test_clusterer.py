"""Tests for clustering module."""

import pytest
from tree_pickup.clusterer import Clusterer
from tree_pickup.models import Address, Coordinate


def test_basic_clustering(sample_address_objects):
    """Test basic clustering with 5 addresses and 3 teams."""
    clusterer = Clusterer()
    team_names = ["Team Alpha", "Team Bravo", "Team Charlie"]

    result = clusterer.cluster_addresses(sample_address_objects, 3, team_names, random_seed=42)

    assert result.num_teams == 3
    assert result.total_addresses == 5
    assert len(result.teams) == 3

    total_assigned = sum(len(team.addresses) for team in result.teams)
    assert total_assigned == 5

    for team in result.teams:
        assert team.name in team_names
        assert team.mst_distance_km >= 0


def test_clustering_single_team_single_address():
    """Test edge case with one team and one address."""
    addresses = [
        Address(
            address_string="123 Main St",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=1,
        )
    ]

    clusterer = Clusterer()
    team_names = ["Team Alpha"]

    result = clusterer.cluster_addresses(addresses, 1, team_names)

    assert len(result.teams) == 1
    assert len(result.teams[0].addresses) == 1
    assert result.teams[0].mst_distance_km == 0.0


def test_clustering_teams_equal_addresses(sample_address_objects):
    """Test when number of teams equals number of addresses."""
    clusterer = Clusterer()
    team_names = [f"Team {i}" for i in range(5)]

    result = clusterer.cluster_addresses(sample_address_objects, 5, team_names)

    assert len(result.teams) == 5

    for team in result.teams:
        assert len(team.addresses) == 1
        assert team.mst_distance_km == 0.0


def test_clustering_reproducibility():
    """Test that same seed produces same results."""
    addresses = [
        Address(
            address_string=f"Address {i}",
            coordinate=Coordinate(latitude=47.5 + i * 0.01, longitude=-122.0 + i * 0.01),
            address_number=i + 1,
        )
        for i in range(10)
    ]

    clusterer = Clusterer()
    team_names = ["Team Alpha", "Team Bravo", "Team Charlie"]

    result1 = clusterer.cluster_addresses(addresses, 3, team_names, random_seed=42)
    result2 = clusterer.cluster_addresses(addresses, 3, team_names, random_seed=42)

    for i in range(3):
        addr_strings_1 = sorted([a.address_string for a in result1.teams[i].addresses])
        addr_strings_2 = sorted([a.address_string for a in result2.teams[i].addresses])
        assert addr_strings_1 == addr_strings_2


def test_clustering_different_seeds():
    """Test that different seeds produce different results."""
    addresses = [
        Address(
            address_string=f"Address {i}",
            coordinate=Coordinate(latitude=47.5 + i * 0.01, longitude=-122.0 + i * 0.01),
            address_number=i + 1,
        )
        for i in range(10)
    ]

    clusterer = Clusterer()
    team_names = ["Team Alpha", "Team Bravo", "Team Charlie"]

    result1 = clusterer.cluster_addresses(addresses, 3, team_names, random_seed=42)
    result2 = clusterer.cluster_addresses(addresses, 3, team_names, random_seed=100)

    all_same = True
    for i in range(3):
        addr_strings_1 = sorted([a.address_string for a in result1.teams[i].addresses])
        addr_strings_2 = sorted([a.address_string for a in result2.teams[i].addresses])
        if addr_strings_1 != addr_strings_2:
            all_same = False
            break

    assert not all_same
