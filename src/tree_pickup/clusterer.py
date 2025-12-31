"""K-Means clustering for geographic assignment."""

import sys

import numpy as np
from rich.console import Console
from sklearn.cluster import KMeans

from tree_pickup.distance import haversine_distance
from tree_pickup.models import Address, ClusterResult, Coordinate, Team
from tree_pickup.mst import calculate_mst_distance
from tree_pickup.validators import detect_outliers

console = Console()

TEAM_COLORS = [
    "red",
    "green",
    "blue",
    "yellow",
    "cyan",
    "magenta",
    "bright_red",
    "bright_green",
    "bright_blue",
    "bright_yellow",
    "bright_cyan",
    "bright_magenta",
]


class Clusterer:
    """K-Means clusterer for geographic address assignment."""

    def cluster_addresses(
        self,
        addresses: list[Address],
        num_teams: int,
        team_names: list[str],
        random_seed: int = 42,
        max_trees: int = 8,
    ) -> ClusterResult:
        """
        Cluster addresses into teams using K-Means with redistribution.

        Args:
            addresses: List of addresses with coordinates
            num_teams: Number of teams to create
            team_names: List of team names (must have length >= num_teams)
            random_seed: Random seed for reproducibility
            max_trees: Maximum addresses per team

        Returns:
            ClusterResult with team assignments

        Raises:
            ValueError: If team_names list is too short
            SystemExit: If redistribution fails
        """
        if len(team_names) < num_teams:
            raise ValueError(
                f"Not enough team names: Expected at least {num_teams} names "
                f"but got {len(team_names)}"
            )
        coordinates = np.array(
            [[addr.coordinate.latitude, addr.coordinate.longitude] for addr in addresses]
        )

        kmeans = KMeans(n_clusters=num_teams, random_state=random_seed, n_init=10)
        labels = kmeans.fit_predict(coordinates)

        team_assignments = {i: [] for i in range(num_teams)}
        for idx, label in enumerate(labels):
            team_assignments[label].append(addresses[idx])

        team_assignments = self._redistribute_addresses(team_assignments, max_trees)

        teams = []
        global_warnings = []

        if num_teams > len(TEAM_COLORS):
            global_warnings.append(
                f"Warning: {num_teams} teams exceed available colors ({len(TEAM_COLORS)}). "
                "Some teams will share colors in visualization."
            )

        # Calculate centroids for smart color assignment
        centroids = {}
        for i in range(num_teams):
            cluster_addresses = team_assignments[i]
            if cluster_addresses:
                avg_lat = sum(addr.coordinate.latitude for addr in cluster_addresses) / len(
                    cluster_addresses
                )
                avg_lng = sum(addr.coordinate.longitude for addr in cluster_addresses) / len(
                    cluster_addresses
                )
                centroids[i] = Coordinate(latitude=avg_lat, longitude=avg_lng)

        # Assign colors - if more teams than colors, space out duplicate colors geographically
        color_assignments = self._assign_colors_optimally(num_teams, centroids)

        for i in range(num_teams):
            cluster_addresses = team_assignments[i]

            mst_distance = calculate_mst_distance(cluster_addresses)

            warnings = detect_outliers(cluster_addresses)

            if mst_distance > 80:
                warnings.append(
                    f"Estimated distance is {mst_distance:.2f} km "
                    f"({mst_distance * 0.621371:.2f} miles) - verify addresses are correct"
                )

            team = Team(
                name=team_names[i],
                addresses=cluster_addresses,
                mst_distance_km=mst_distance,
                warnings=warnings,
                color=color_assignments[i],
            )

            teams.append(team)

        return ClusterResult(
            teams=teams,
            total_addresses=len(addresses),
            num_teams=num_teams,
            global_warnings=global_warnings,
        )

    def _redistribute_addresses(
        self, team_assignments: dict[int, list[Address]], max_trees: int
    ) -> dict[int, list[Address]]:
        """
        Redistribute addresses to enforce max_trees constraint.

        Args:
            team_assignments: Dict mapping team index to list of addresses
            max_trees: Maximum addresses per team

        Returns:
            Updated team assignments with all teams <= max_trees

        Raises:
            SystemExit: If redistribution is impossible or fails
        """
        overloaded = [i for i in team_assignments if len(team_assignments[i]) > max_trees]

        if not overloaded:
            return team_assignments

        if len(team_assignments) == 1:
            count = len(team_assignments[0])
            console.print(
                f"[red][ERROR] Cannot redistribute: Only 1 team with {count} addresses "
                f"exceeds max-trees limit of {max_trees}. Increase --teams or --max-trees.[/red]"
            )
            sys.exit(1)

        if all(len(addrs) >= max_trees for addrs in team_assignments.values()):
            console.print(
                "[red][ERROR] Cannot redistribute: All teams at or above capacity. "
                "Increase --teams or --max-trees.[/red]"
            )
            sys.exit(1)

        max_iterations = 1000
        iteration_count = 0

        while any(len(team_assignments[i]) > max_trees for i in team_assignments) and iteration_count < max_iterations:
            overloaded_teams = [i for i in team_assignments if len(team_assignments[i]) > max_trees]
            most_overloaded = max(overloaded_teams, key=lambda i: len(team_assignments[i]))

            centroids = {}
            for i in team_assignments:
                if team_assignments[i]:
                    avg_lat = sum(addr.coordinate.latitude for addr in team_assignments[i]) / len(
                        team_assignments[i]
                    )
                    avg_lng = sum(addr.coordinate.longitude for addr in team_assignments[i]) / len(
                        team_assignments[i]
                    )
                    centroids[i] = Coordinate(latitude=avg_lat, longitude=avg_lng)

            best_address = None
            best_target_team = None
            best_distance = float("inf")

            for address in team_assignments[most_overloaded]:
                for target_team in team_assignments:
                    if target_team != most_overloaded and len(team_assignments[target_team]) < max_trees:
                        if target_team in centroids:
                            distance = haversine_distance(address.coordinate, centroids[target_team])
                        else:
                            distance = 0.0

                        if distance < best_distance:
                            best_distance = distance
                            best_address = address
                            best_target_team = target_team

            if best_address is None or best_target_team is None:
                console.print(
                    "[red][ERROR] Redistribution failed: Could not find valid move. "
                    "Try increasing --max-trees or --teams.[/red]"
                )
                sys.exit(1)

            team_assignments[most_overloaded].remove(best_address)
            team_assignments[best_target_team].append(best_address)

            iteration_count += 1

        if iteration_count >= max_iterations:
            console.print(
                "[red][ERROR] Redistribution failed: Could not balance teams after 1000 iterations. "
                "Try increasing --max-trees or --teams.[/red]"
            )
            sys.exit(1)

        if iteration_count > 0:
            console.print(
                f"[yellow]Note: Redistribution required {iteration_count} iterations to balance teams. "
                f"Geographic optimality may be reduced compared to pure K-Means clustering.[/yellow]"
            )

        return team_assignments

    def _assign_colors_optimally(
        self, num_teams: int, centroids: dict[int, Coordinate]
    ) -> dict[int, str]:
        """
        Assign colors to teams, spacing out duplicate colors geographically.

        Args:
            num_teams: Number of teams
            centroids: Dict mapping team index to centroid coordinate

        Returns:
            Dict mapping team index to color string
        """
        color_assignments = {}

        # If we have enough colors, assign sequentially
        if num_teams <= len(TEAM_COLORS):
            for i in range(num_teams):
                color_assignments[i] = TEAM_COLORS[i]
            return color_assignments

        # Otherwise, use smart assignment to space out duplicate colors
        # First, assign one color to each team using a greedy approach
        teams_by_color = {color: [] for color in TEAM_COLORS}

        # Assign first batch of colors directly
        for i in range(len(TEAM_COLORS)):
            color_assignments[i] = TEAM_COLORS[i]
            teams_by_color[TEAM_COLORS[i]].append(i)

        # For remaining teams, assign them to colors where they're furthest
        # from existing teams with that color
        for team_idx in range(len(TEAM_COLORS), num_teams):
            if team_idx not in centroids:
                # Team has no addresses, assign next color in sequence
                color_assignments[team_idx] = TEAM_COLORS[team_idx % len(TEAM_COLORS)]
                continue

            best_color = None
            best_min_distance = -1

            # For each color, find the minimum distance to any team already using that color
            for color in TEAM_COLORS:
                min_distance_to_color = float("inf")

                for existing_team_idx in teams_by_color[color]:
                    if existing_team_idx in centroids:
                        distance = haversine_distance(
                            centroids[team_idx], centroids[existing_team_idx]
                        )
                        min_distance_to_color = min(min_distance_to_color, distance)

                # Choose the color where this team is furthest from existing teams with that color
                if min_distance_to_color > best_min_distance:
                    best_min_distance = min_distance_to_color
                    best_color = color

            color_assignments[team_idx] = best_color
            teams_by_color[best_color].append(team_idx)

        return color_assignments
