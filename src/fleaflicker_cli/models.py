"""Data models for Fleaflicker API responses."""

from dataclasses import dataclass, field


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


@dataclass
class TeamStanding:
    """A team's standing in the league."""

    team_id: int
    team_name: str
    division: str = ""
    wins: int = 0
    losses: int = 0
    points_for: str = "0"
    points_against: str = "0"
    draft_position: int | None = None
    owner_display_names: list[str] = field(default_factory=list)
    activity_unread: int = 0
    trades_pending: int = 0
