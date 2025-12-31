"""Tests for file_exporter module."""

from pathlib import Path

from tree_pickup.file_exporter import export_to_file
from tree_pickup.models import Address, ClusterResult, Coordinate, Team


def test_export_to_file_creates_file(tmp_path):
    """Test that export creates a file with correct name format."""
    coord = Coordinate(latitude=47.6, longitude=-122.3)
    addr1 = Address(address_string="123 Main St", coordinate=coord, address_number=1)
    addr2 = Address(address_string="456 Oak Ave", coordinate=coord, address_number=2)

    team = Team(name="Alpha", addresses=[addr1, addr2], mst_distance_km=5.0, color="red")
    result = ClusterResult(teams=[team], total_addresses=2, num_teams=1)

    filepath = export_to_file(result, max_trees=8, output_dir=str(tmp_path))

    assert filepath
    assert Path(filepath).exists()
    assert "tree-pickup-results" in filepath
    assert "1teams" in filepath
    assert "2addrs" in filepath


def test_export_file_content_format(tmp_path):
    """Test file content has correct format."""
    coord = Coordinate(latitude=47.6, longitude=-122.3)
    addr1 = Address(address_string="123 Main St", coordinate=coord, address_number=1)
    addr2 = Address(address_string="456 Oak Ave", coordinate=coord, address_number=2)

    team = Team(name="Alpha", addresses=[addr1, addr2], mst_distance_km=5.0, color="red")
    result = ClusterResult(teams=[team], total_addresses=2, num_teams=1)

    filepath = export_to_file(result, max_trees=8, output_dir=str(tmp_path))

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Tree Pickup Results" in content
    assert "Date:" in content
    assert "Teams: 1" in content
    assert "Addresses: 2" in content
    assert "Max Trees per Team: 8" in content
    assert "Team Alpha" in content
    assert "123 Main St" in content
    assert "456 Oak Ave" in content


def test_export_multiple_teams(tmp_path):
    """Test export with multiple teams."""
    coord = Coordinate(latitude=47.6, longitude=-122.3)
    addr1 = Address(address_string="123 Main St", coordinate=coord, address_number=1)
    addr2 = Address(address_string="456 Oak Ave", coordinate=coord, address_number=2)

    team1 = Team(name="Alpha", addresses=[addr1], mst_distance_km=5.0, color="red")
    team2 = Team(name="Bravo", addresses=[addr2], mst_distance_km=3.0, color="green")
    result = ClusterResult(teams=[team1, team2], total_addresses=2, num_teams=2)

    filepath = export_to_file(result, max_trees=8, output_dir=str(tmp_path))

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Team Alpha" in content
    assert "Team Bravo" in content
    assert "123 Main St" in content
    assert "456 Oak Ave" in content


def test_export_handles_invalid_directory():
    """Test export handles invalid output directory gracefully."""
    coord = Coordinate(latitude=47.6, longitude=-122.3)
    addr = Address(address_string="123 Main St", coordinate=coord, address_number=1)
    team = Team(name="Alpha", addresses=[addr], mst_distance_km=5.0, color="red")
    result = ClusterResult(teams=[team], total_addresses=1, num_teams=1)

    filepath = export_to_file(result, max_trees=8, output_dir="/invalid/path/does/not/exist")

    assert filepath == ""
