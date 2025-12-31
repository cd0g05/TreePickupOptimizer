"""Tests for team name generator module."""

import pytest
from tree_pickup.team_generator import generate_team_names


def test_generate_single_team():
    """Test generation of single team name."""
    names = generate_team_names(1)

    assert len(names) == 1
    assert names[0] == "Team Alpha"


def test_generate_five_teams():
    """Test generation of five team names."""
    names = generate_team_names(5)

    assert len(names) == 5
    assert names[0] == "Team Alpha"
    assert names[1] == "Team Bravo"
    assert names[2] == "Team Charlie"
    assert names[3] == "Team Delta"
    assert names[4] == "Team Echo"


def test_generate_twenty_six_teams():
    """Test generation of 26 teams (full alphabet)."""
    names = generate_team_names(26)

    assert len(names) == 26
    assert names[0] == "Team Alpha"
    assert names[25] == "Team Zulu"


def test_generate_more_than_alphabet():
    """Test generation beyond 26 teams."""
    names = generate_team_names(30)

    assert len(names) == 30
    assert names[0] == "Team Alpha"
    assert names[25] == "Team Zulu"
    assert names[26] == "Team Alpha 2"
    assert names[27] == "Team Bravo 2"
    assert names[29] == "Team Delta 2"


def test_generate_uniqueness():
    """Test that all generated names are unique."""
    names = generate_team_names(100)

    assert len(names) == len(set(names))


def test_generate_deterministic():
    """Test that generation is deterministic."""
    names1 = generate_team_names(10)
    names2 = generate_team_names(10)

    assert names1 == names2
