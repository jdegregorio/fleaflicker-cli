"""Data models for Fleaflicker API responses."""

from dataclasses import dataclass


@dataclass
class Player:
    """A player on a fantasy roster."""

    name: str
    position: str
    nfl_team: str | None = None
    fleaflicker_id: str | None = None


@dataclass
class DraftPick:
    """A draft pick, possibly traded."""

    season: int
    round: int
    slot: int | None = None
    original_owner: str = "Unknown"
    current_owner: str = "Unknown"
    lost: bool = False
