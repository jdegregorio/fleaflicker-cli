"""HTTP client for the Fleaflicker fantasy football API."""

import requests

from fleaflicker_cli.models import DraftPick, Player

BASE_URL = "https://www.fleaflicker.com/api"


class FleaflickerClient:
    """Generic client for the Fleaflicker public API."""

    def __init__(self, base_url: str = BASE_URL, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, endpoint: str, **params) -> dict:
        """Make a GET request to the Fleaflicker API."""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    # ── Fetch helpers ──────────────────────────────────────────────

    def fetch_standings(self, league_id: int) -> dict:
        """Fetch league standings."""
        return self.get("FetchLeagueStandings", league_id=league_id)

    def fetch_roster(self, league_id: int, team_id: int) -> dict:
        """Fetch a single team's roster."""
        return self.get("FetchRoster", league_id=league_id, team_id=team_id)

    def fetch_team_picks(self, league_id: int, team_id: int) -> dict:
        """Fetch draft picks owned by a team."""
        return self.get("FetchTeamPicks", league_id=league_id, team_id=team_id)

    def fetch_league_rosters(self, league_id: int) -> dict:
        """Fetch all rosters in a league."""
        return self.get("FetchLeagueRosters", league_id=league_id)

    # ── Parsing helpers ────────────────────────────────────────────

    @staticmethod
    def parse_roster_players(roster_payload: dict) -> list[Player]:
        """Parse a FetchRoster response into Player objects."""
        players: list[Player] = []
        for group in roster_payload.get("groups", []):
            for slot in group.get("slots", []):
                league_player = slot.get("leaguePlayer") or {}
                pro = league_player.get("proPlayer") or {}
                if not pro:
                    continue
                players.append(
                    Player(
                        name=pro.get("nameFull", "Unknown"),
                        position=pro.get("position", "UNK"),
                        nfl_team=pro.get("proTeamAbbreviation"),
                        fleaflicker_id=(
                            str(pro["id"]) if pro.get("id") is not None else None
                        ),
                    )
                )
        return players

    @staticmethod
    def parse_team_picks(picks_payload: dict) -> list[DraftPick]:
        """Parse a FetchTeamPicks response into DraftPick objects."""
        picks: list[DraftPick] = []
        for pick in picks_payload.get("picks", []):
            slot = pick.get("slot") or {}
            original_owner = (pick.get("originalOwner") or {}).get("name", "Unknown")
            current_owner = (pick.get("ownedBy") or {}).get("name", "Unknown")
            picks.append(
                DraftPick(
                    season=int(pick.get("season")),
                    round=int(slot.get("round")),
                    slot=slot.get("slot"),
                    original_owner=original_owner,
                    current_owner=current_owner,
                    lost=bool(pick.get("lost")),
                )
            )
        return picks

    @staticmethod
    def find_team_standing(standings_payload: dict, team_id: int) -> dict:
        """Find a specific team within a standings response."""
        for division in standings_payload.get("divisions", []):
            for team in division.get("teams", []):
                if team.get("id") == team_id:
                    return team
        return {}
