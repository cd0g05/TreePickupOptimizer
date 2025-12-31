"""ASCII map visualization for tree pickup results."""

from rich.console import Console

from tree_pickup.models import ClusterResult


def create_ascii_map(result: ClusterResult, console: Console) -> None:
    """
    Create ASCII map visualization of team assignments.

    Args:
        result: ClusterResult to visualize
        console: Rich Console for output
    """
    if console.width < 40 or console.height < 20:
        console.print(
            "[yellow]Terminal too small for visualization (min 40x20). Skipping map.[/yellow]"
        )
        return

    all_addresses = []
    for team in result.teams:
        for address in team.addresses:
            all_addresses.append((address, team.name, team.color))

    if not all_addresses:
        return

    lats = [addr.coordinate.latitude for addr, _, _ in all_addresses]
    lngs = [addr.coordinate.longitude for addr, _, _ in all_addresses]

    min_lat, max_lat = min(lats), max(lats)
    min_lng, max_lng = min(lngs), max(lngs)

    if max_lng == min_lng and max_lat == min_lat:
        console.print(
            "[yellow]All addresses at same location. Showing simplified visualization.[/yellow]"
        )
        console.print(f"[{all_addresses[0][2]}]*[/{all_addresses[0][2]}] ({len(all_addresses)} addresses)")
        return

    width = console.width - 20
    height = console.height - 10

    if max_lng == min_lng:
        console.print(
            "[yellow]All addresses at same longitude. Showing simplified visualization.[/yellow]"
        )
        grid: dict[tuple[int, int], tuple[str, str]] = {}
        for i, (addr, team_name, color) in enumerate(all_addresses):
            y = int((max_lat - addr.coordinate.latitude) / (max_lat - min_lat) * height) if max_lat != min_lat else height // 2
            x = width // 2
            if (x, y) not in grid:
                grid[(x, y)] = (team_name, color)
    elif max_lat == min_lat:
        console.print(
            "[yellow]All addresses at same latitude. Showing simplified visualization.[/yellow]"
        )
        grid = {}
        for i, (addr, team_name, color) in enumerate(all_addresses):
            x = int((addr.coordinate.longitude - min_lng) / (max_lng - min_lng) * width)
            y = height // 2
            if (x, y) not in grid:
                grid[(x, y)] = (team_name, color)
    else:
        grid = {}
        for addr, team_name, color in all_addresses:
            x = int((addr.coordinate.longitude - min_lng) / (max_lng - min_lng) * width)
            y = int((max_lat - addr.coordinate.latitude) / (max_lat - min_lat) * height)

            if (x, y) not in grid:
                grid[(x, y)] = (team_name, color)

    console.print("+" + "-" * (width + 2) + "+")
    for y in range(height):
        row = "|"
        for x in range(width):
            if (x, y) in grid:
                _, color = grid[(x, y)]
                row += f"[{color}]*[/{color}]"
            else:
                row += " "
        row += " |"
        console.print(row)
    console.print("+" + "-" * (width + 2) + "+")

    legend_parts = []
    for team in result.teams:
        legend_parts.append(f"[{team.color}]{team.name}: *[/{team.color}]")

    console.print("  ".join(legend_parts))
