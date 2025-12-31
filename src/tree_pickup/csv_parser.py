"""CSV parsing and validation for address input."""

import csv
import sys
from pathlib import Path


def normalize_address(address: str) -> str:
    """Normalize address for duplicate detection."""
    return " ".join(address.lower().strip().split())


def parse_addresses(file_path: str) -> list[str]:
    """
    Parse addresses from CSV file with validation.

    Args:
        file_path: Path to CSV file with 'address' column

    Returns:
        List of address strings

    Raises:
        SystemExit: On validation errors (missing file, no header, no addresses, duplicates)
    """
    path = Path(file_path)

    if not path.exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                print("[ERROR] CSV missing header row. Add a header row with 'address' column.")
                sys.exit(1)

            if "address" not in reader.fieldnames:
                print(
                    "[ERROR] CSV missing 'address' column. "
                    "Ensure your CSV has a header row with an 'address' column."
                )
                sys.exit(1)

            addresses = []
            seen_normalized = set()

            for row in reader:
                address = row["address"].strip()
                if not address:
                    continue

                normalized = normalize_address(address)

                if normalized in seen_normalized:
                    print(
                        f"[ERROR] Duplicate address found: '{address}'. "
                        "Remove duplicates and try again."
                    )
                    sys.exit(1)

                seen_normalized.add(normalized)
                addresses.append(address)

            if not addresses:
                print("[ERROR] CSV contains no addresses. Add addresses to your CSV file.")
                sys.exit(1)

            return addresses

    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)
    except PermissionError:
        print(f"[ERROR] Permission denied: Cannot read {file_path}. Check file permissions.")
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(
            f"[ERROR] File encoding error: {file_path} contains invalid characters. "
            f"Ensure the file is saved as UTF-8. Details: {e}"
        )
        sys.exit(1)
    except csv.Error as e:
        print(f"[ERROR] CSV format error: {e}. Check that the file is a valid CSV.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error reading CSV file: {e}")
        sys.exit(1)
