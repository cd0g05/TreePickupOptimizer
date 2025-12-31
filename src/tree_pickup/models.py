"""Data models for tree pickup assignment optimizer."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Coordinate(BaseModel):
    """Geographic coordinate with validation."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class Address(BaseModel):
    """Address with optional geocoded coordinate."""

    address_string: str
    coordinate: Optional[Coordinate] = None
    address_number: int

    @field_validator("address_string")
    @classmethod
    def validate_address_string(cls, v: str) -> str:
        """Ensure address string is not empty."""
        if not v.strip():
            raise ValueError("Address string cannot be empty")
        return v.strip()


class Team(BaseModel):
    """Team with assigned addresses and distance metrics."""

    name: str
    addresses: list[Address]
    mst_distance_km: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    color: str = ""


class ClusterResult(BaseModel):
    """Complete clustering result with all teams."""

    teams: list[Team]
    total_addresses: int
    num_teams: int
    global_warnings: list[str] = Field(default_factory=list)
