"""Plain text file export for tree pickup results."""

from datetime import datetime
from pathlib import Path

from rich.console import Console

from tree_pickup.models import ClusterResult

console = Console()


def export_to_file(result: ClusterResult, max_trees: int, output_dir: str = ".") -> str:
    """
    Export clustering results to plain text file.

    Args:
        result: ClusterResult to export
        max_trees: Maximum addresses per team
        output_dir: Directory to save file (default: current directory)

    Returns:
        Full path to exported file, or empty string if failed
    """
    now = datetime.now()
    datetime_readable = now.strftime("%Y-%m-%d %H:%M:%S")
    datetime_filename = now.strftime("%Y%m%d-%H%M%S")

    filename = (
        f"tree-pickup-results-{datetime_filename}-"
        f"{result.num_teams}teams-{result.total_addresses}addrs.txt"
    )

    output_path = Path(output_dir)

    if output_path.exists() and not output_path.is_dir():
        console.print(
            f"[yellow]Warning: Could not save results to file: '{output_dir}' exists but is not a directory. "
            f"Results displayed above.[/yellow]"
        )
        return ""

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError, IOError) as e:
        console.print(
            f"[yellow]Warning: Could not save results to file: {e}. Results displayed above.[/yellow]"
        )
        return ""

    file_path = output_path / filename

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Tree Pickup Results\n")
            f.write(f"Date: {datetime_readable}\n")
            f.write(f"Teams: {result.num_teams}\n")
            f.write(f"Addresses: {result.total_addresses}\n")
            f.write(f"Max Trees per Team: {max_trees}\n")
            f.write("\n")

            for team in result.teams:
                f.write(f"{team.name}\n")
                for address in team.addresses:
                    f.write(f"    {address.address_string}\n")
                f.write("\n")

        return str(file_path.absolute())

    except (OSError, PermissionError, IOError) as e:
        console.print(
            f"[yellow]Warning: Could not save results to file: {e}. Results displayed above.[/yellow]"
        )
        return ""
