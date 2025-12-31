"""Tests for CSV parser module."""

import pytest
from pathlib import Path
from tree_pickup.csv_parser import parse_addresses, normalize_address


def test_normalize_address():
    """Test address normalization."""
    assert normalize_address("  123  Main   St  ") == "123 main st"
    assert normalize_address("UPPER CASE") == "upper case"
    assert normalize_address("Mixed   Spaces") == "mixed spaces"


def test_parse_valid_csv(tmp_path):
    """Test parsing valid CSV file."""
    csv_file = tmp_path / "addresses.csv"
    csv_file.write_text("address\n123 Main St\n456 Elm St\n")

    addresses = parse_addresses(str(csv_file))

    assert len(addresses) == 2
    assert addresses[0] == "123 Main St"
    assert addresses[1] == "456 Elm St"


def test_parse_missing_file():
    """Test error when file doesn't exist."""
    with pytest.raises(SystemExit) as exc_info:
        parse_addresses("nonexistent.csv")

    assert exc_info.value.code == 1


def test_parse_csv_without_header(tmp_path):
    """Test error when CSV has no header."""
    csv_file = tmp_path / "no_header.csv"
    csv_file.write_text("")

    with pytest.raises(SystemExit) as exc_info:
        parse_addresses(str(csv_file))

    assert exc_info.value.code == 1


def test_parse_csv_missing_address_column(tmp_path):
    """Test error when CSV missing 'address' column."""
    csv_file = tmp_path / "wrong_column.csv"
    csv_file.write_text("location\n123 Main St\n")

    with pytest.raises(SystemExit) as exc_info:
        parse_addresses(str(csv_file))

    assert exc_info.value.code == 1


def test_parse_empty_csv(tmp_path):
    """Test error when CSV has header but no data."""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("address\n")

    with pytest.raises(SystemExit) as exc_info:
        parse_addresses(str(csv_file))

    assert exc_info.value.code == 1


def test_parse_csv_with_duplicates(tmp_path):
    """Test error when CSV contains duplicate addresses."""
    csv_file = tmp_path / "duplicates.csv"
    csv_file.write_text("address\n123 Main St\n456 Elm St\n123 Main St\n")

    with pytest.raises(SystemExit) as exc_info:
        parse_addresses(str(csv_file))

    assert exc_info.value.code == 1


def test_parse_csv_with_whitespace_duplicates(tmp_path):
    """Test duplicate detection with different whitespace."""
    csv_file = tmp_path / "whitespace_dups.csv"
    csv_file.write_text("address\n123 Main St\n  123   Main   St  \n")

    with pytest.raises(SystemExit) as exc_info:
        parse_addresses(str(csv_file))

    assert exc_info.value.code == 1


def test_parse_csv_skips_empty_rows(tmp_path):
    """Test that empty rows are skipped."""
    csv_file = tmp_path / "empty_rows.csv"
    csv_file.write_text("address\n123 Main St\n\n456 Elm St\n")

    addresses = parse_addresses(str(csv_file))

    assert len(addresses) == 2
    assert addresses[0] == "123 Main St"
    assert addresses[1] == "456 Elm St"
