"""Tests for CLI module."""

import pytest
from unittest.mock import Mock, patch
from tree_pickup.cli import main
from tree_pickup.models import Coordinate


@patch("tree_pickup.cli.Geocoder")
@patch("tree_pickup.cli.parse_addresses")
def test_cli_happy_path(mock_parse, mock_geocoder_class, tmp_path, capsys):
    """Test CLI end-to-end happy path."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("address\n123 Main St\n456 Elm St\n789 Oak Ave\n")

    mock_parse.return_value = ["123 Main St", "456 Elm St", "789 Oak Ave"]

    mock_geocoder = Mock()
    mock_geocoder_class.return_value = mock_geocoder
    mock_geocoder.geocode_addresses.return_value = [
        Coordinate(latitude=47.5, longitude=-122.0),
        Coordinate(latitude=47.501, longitude=-122.001),
        Coordinate(latitude=47.502, longitude=-122.002),
    ]

    with patch("sys.argv", ["tree-pickup", "--addresses", str(csv_file), "--teams", "2"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0


@patch("tree_pickup.cli.parse_addresses")
def test_cli_missing_addresses_file(mock_parse):
    """Test CLI with missing addresses file."""
    mock_parse.side_effect = SystemExit(1)

    with patch("sys.argv", ["tree-pickup", "--addresses", "nonexistent.csv", "--teams", "2"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


@patch("tree_pickup.cli.parse_addresses")
@patch("tree_pickup.cli.validate_team_count")
def test_cli_invalid_team_count(mock_validate, mock_parse, tmp_path):
    """Test CLI with too many teams."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("address\n123 Main St\n")

    mock_parse.return_value = ["123 Main St"]
    mock_validate.side_effect = SystemExit(1)

    with patch("sys.argv", ["tree-pickup", "--addresses", str(csv_file), "--teams", "10"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


@patch("tree_pickup.cli.Geocoder")
@patch("tree_pickup.cli.parse_addresses")
def test_cli_custom_seed(mock_parse, mock_geocoder_class, tmp_path):
    """Test CLI with custom seed."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("address\n123 Main St\n456 Elm St\n")

    mock_parse.return_value = ["123 Main St", "456 Elm St"]

    mock_geocoder = Mock()
    mock_geocoder_class.return_value = mock_geocoder
    mock_geocoder.geocode_addresses.return_value = [
        Coordinate(latitude=47.5, longitude=-122.0),
        Coordinate(latitude=47.6, longitude=-122.1),
    ]

    with patch("sys.argv", ["tree-pickup", "--addresses", str(csv_file), "--teams", "2", "--seed", "100"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0


@patch("tree_pickup.cli.Geocoder")
@patch("tree_pickup.cli.parse_addresses")
def test_cli_custom_cache_file(mock_parse, mock_geocoder_class, tmp_path):
    """Test CLI with custom cache file."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("address\n123 Main St\n")
    cache_file = tmp_path / "custom_cache.json"

    mock_parse.return_value = ["123 Main St"]

    mock_geocoder = Mock()
    mock_geocoder_class.return_value = mock_geocoder
    mock_geocoder.geocode_addresses.return_value = [
        Coordinate(latitude=47.5, longitude=-122.0),
    ]

    with patch(
        "sys.argv",
        [
            "tree-pickup",
            "--addresses",
            str(csv_file),
            "--teams",
            "1",
            "--cache-file",
            str(cache_file),
        ],
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    mock_geocoder.geocode_addresses.assert_called_once()
    assert mock_geocoder.geocode_addresses.call_args[0][1] == str(cache_file)
