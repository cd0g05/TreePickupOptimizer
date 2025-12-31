"""Tests for visualizer module."""

from io import StringIO

from rich.console import Console

from tree_pickup.models import Address, ClusterResult, Coordinate, Team
from tree_pickup.visualizer import create_ascii_map


def test_visualizer_with_normal_coordinates():
    """Test visualization with spread out coordinates."""
    coord1 = Coordinate(latitude=47.6, longitude=-122.3)
    coord2 = Coordinate(latitude=47.7, longitude=-122.0)

    addr1 = Address(address_string="123 Main St", coordinate=coord1, address_number=1)
    addr2 = Address(address_string="456 Oak Ave", coordinate=coord2, address_number=2)

    team1 = Team(name="Alpha", addresses=[addr1], mst_distance_km=5.0, color="red")
    team2 = Team(name="Bravo", addresses=[addr2], mst_distance_km=3.0, color="green")
    result = ClusterResult(teams=[team1, team2], total_addresses=2, num_teams=2)

    output = StringIO()
    console = Console(file=output, width=80, height=40, force_terminal=True)

    create_ascii_map(result, console)

    output_text = output.getvalue()

    assert "+" in output_text
    assert "Team Alpha" in output_text
    assert "Team Bravo" in output_text


def test_visualizer_identical_coordinates():
    """Test visualization with all addresses at same location."""
    coord = Coordinate(latitude=47.6, longitude=-122.3)

    addr1 = Address(address_string="123 Main St", coordinate=coord, address_number=1)
    addr2 = Address(address_string="456 Oak Ave", coordinate=coord, address_number=2)

    team = Team(name="Alpha", addresses=[addr1, addr2], mst_distance_km=0.0, color="red")
    result = ClusterResult(teams=[team], total_addresses=2, num_teams=1)

    output = StringIO()
    console = Console(file=output, width=80, height=40, force_terminal=True)

    create_ascii_map(result, console)

    output_text = output.getvalue()

    assert "same location" in output_text.lower()


def test_visualizer_same_longitude():
    """Test visualization with all addresses at same longitude."""
    coord1 = Coordinate(latitude=47.6, longitude=-122.3)
    coord2 = Coordinate(latitude=47.7, longitude=-122.3)

    addr1 = Address(address_string="123 Main St", coordinate=coord1, address_number=1)
    addr2 = Address(address_string="456 Oak Ave", coordinate=coord2, address_number=2)

    team = Team(name="Alpha", addresses=[addr1, addr2], mst_distance_km=5.0, color="red")
    result = ClusterResult(teams=[team], total_addresses=2, num_teams=1)

    output = StringIO()
    console = Console(file=output, width=80, height=40, force_terminal=True)

    create_ascii_map(result, console)

    output_text = output.getvalue()

    assert "same longitude" in output_text.lower()


def test_visualizer_same_latitude():
    """Test visualization with all addresses at same latitude."""
    coord1 = Coordinate(latitude=47.6, longitude=-122.3)
    coord2 = Coordinate(latitude=47.6, longitude=-122.0)

    addr1 = Address(address_string="123 Main St", coordinate=coord1, address_number=1)
    addr2 = Address(address_string="456 Oak Ave", coordinate=coord2, address_number=2)

    team = Team(name="Alpha", addresses=[addr1, addr2], mst_distance_km=5.0, color="red")
    result = ClusterResult(teams=[team], total_addresses=2, num_teams=1)

    output = StringIO()
    console = Console(file=output, width=80, height=40, force_terminal=True)

    create_ascii_map(result, console)

    output_text = output.getvalue()

    assert "same latitude" in output_text.lower()


def test_visualizer_terminal_too_small():
    """Test visualization when terminal is too small."""
    coord = Coordinate(latitude=47.6, longitude=-122.3)
    addr = Address(address_string="123 Main St", coordinate=coord, address_number=1)
    team = Team(name="Alpha", addresses=[addr], mst_distance_km=0.0, color="red")
    result = ClusterResult(teams=[team], total_addresses=1, num_teams=1)

    output = StringIO()
    console = Console(file=output, width=30, height=10, force_terminal=True)

    create_ascii_map(result, console)

    output_text = output.getvalue()

    assert "too small" in output_text.lower()
