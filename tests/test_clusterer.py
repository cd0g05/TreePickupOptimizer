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


def test_redistribution_enforces_max_trees():
    """Test redistribution moves addresses to enforce max_trees."""
    addresses = []
    for i in range(20):
        if i < 12:
            lat = 47.5
            lng = -122.0
        else:
            lat = 47.6
            lng = -122.1

        addresses.append(
            Address(
                address_string=f"Address {i}",
                coordinate=Coordinate(latitude=lat, longitude=lng),
                address_number=i + 1,
            )
        )

    clusterer = Clusterer()
    team_names = ["Team Alpha", "Team Bravo", "Team Charlie"]

    result = clusterer.cluster_addresses(addresses, 3, team_names, random_seed=42, max_trees=8)

    for team in result.teams:
        assert len(team.addresses) <= 8


def test_redistribution_color_assignment():
    """Test that teams are assigned colors correctly."""
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

    result = clusterer.cluster_addresses(addresses, 3, team_names)

    assert result.teams[0].color == "red"
    assert result.teams[1].color == "green"
    assert result.teams[2].color == "blue"


def test_redistribution_one_team_exceeds_max():
    """Test redistribution fails when only 1 team exceeds max."""
    addresses = [
        Address(
            address_string=f"Address {i}",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0),
            address_number=i + 1,
        )
        for i in range(10)
    ]

    clusterer = Clusterer()
    team_names = ["Team Alpha"]

    with pytest.raises(SystemExit) as exc_info:
        clusterer.cluster_addresses(addresses, 1, team_names, max_trees=8)

    assert exc_info.value.code == 1


def test_redistribution_all_teams_at_capacity():
    """Test redistribution succeeds when there's exactly capacity."""
    # 16 addresses with 2 teams and max_trees=8 should work perfectly
    addresses = [
        Address(
            address_string=f"Address {i}",
            coordinate=Coordinate(latitude=47.5, longitude=-122.0 + i * 0.001),
            address_number=i + 1,
        )
        for i in range(16)
    ]

    clusterer = Clusterer()
    team_names = ["Team Alpha", "Team Bravo"]

    result = clusterer.cluster_addresses(addresses, 2, team_names, random_seed=42, max_trees=8)

    # Should succeed and all teams should be at or below capacity
    for team in result.teams:
        assert len(team.addresses) <= 8


def test_color_exhaustion_warning():
    """Test that warning is issued when teams exceed available colors."""
    addresses = [
        Address(
            address_string=f"Address {i}",
            coordinate=Coordinate(latitude=47.5 + i * 0.001, longitude=-122.0 + i * 0.001),
            address_number=i + 1,
        )
        for i in range(15)
    ]

    clusterer = Clusterer()
    team_names = [f"Team {i}" for i in range(15)]

    result = clusterer.cluster_addresses(addresses, 15, team_names, random_seed=42)

    assert len(result.global_warnings) > 0
    assert any("exceed available colors" in w for w in result.global_warnings)
