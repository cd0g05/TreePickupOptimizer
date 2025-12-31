"""K-Means clustering for geographic assignment."""

import numpy as np
from sklearn.cluster import KMeans

from tree_pickup.models import Address, ClusterResult, Team
from tree_pickup.mst import calculate_mst_distance
from tree_pickup.validators import detect_outliers


class Clusterer:
    """K-Means clusterer for geographic address assignment."""

    def cluster_addresses(
        self, addresses: list[Address], num_teams: int, team_names: list[str], random_seed: int = 42
    ) -> ClusterResult:
        """
        Cluster addresses into teams using K-Means.

        Args:
            addresses: List of addresses with coordinates
            num_teams: Number of teams to create
            team_names: List of team names (must have length >= num_teams)
            random_seed: Random seed for reproducibility

        Returns:
            ClusterResult with team assignments

        Raises:
            ValueError: If team_names list is too short
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

        teams = []
        global_warnings = []

        for i in range(num_teams):
            cluster_indices = np.where(labels == i)[0]
            cluster_addresses = [addresses[idx] for idx in cluster_indices]

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
            )

            teams.append(team)

        return ClusterResult(
            teams=teams,
            total_addresses=len(addresses),
            num_teams=num_teams,
            global_warnings=global_warnings,
        )
