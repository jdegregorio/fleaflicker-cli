"""Tests for FleaflickerClient parsing and HTTP methods."""

import responses

from fleaflicker_cli.client import BASE_URL, FleaflickerClient

SAMPLE_ROSTER = {
    "groups": [
        {
            "slots": [
                {
                    "leaguePlayer": {
                        "proPlayer": {
                            "id": 1001,
                            "nameFull": "Patrick Mahomes",
                            "position": "QB",
                            "proTeamAbbreviation": "KC",
                        }
                    }
                },
                {
                    "leaguePlayer": {
                        "proPlayer": {
                            "id": 1002,
                            "nameFull": "Derrick Henry",
                            "position": "RB",
                            "proTeamAbbreviation": "BAL",
                        }
                    }
                },
                # Empty slot (no proPlayer)
                {"leaguePlayer": {"proPlayer": {}}},
                # Missing leaguePlayer entirely
                {},
            ]
        }
    ]
}

SAMPLE_PICKS = {
    "picks": [
        {
            "season": "2026",
            "slot": {"round": "1", "slot": 5},
            "originalOwner": {"name": "Team Alpha"},
            "ownedBy": {"name": "Team Beta"},
            "lost": False,
        },
        {
            "season": "2026",
            "slot": {"round": "2", "slot": 12},
            "originalOwner": {"name": "Team Beta"},
            "ownedBy": {"name": "Team Beta"},
            "lost": False,
        },
        {
            "season": "2027",
            "slot": {"round": "1"},
            "originalOwner": {"name": "Team Alpha"},
            "ownedBy": {"name": "Team Gamma"},
            "lost": True,
        },
    ]
}

SAMPLE_STANDINGS = {
    "divisions": [
        {
            "name": "Division A",
            "teams": [
                {"id": 100, "name": "Team Alpha"},
                {"id": 200, "name": "Team Beta"},
            ],
        },
        {
            "name": "Division B",
            "teams": [
                {"id": 300, "name": "Team Gamma"},
            ],
        },
    ]
}

SAMPLE_STANDINGS_RICH = {
    "divisions": [
        {
            "name": "Gow Football Conference",
            "teams": [
                {
                    "id": 100,
                    "name": "Seattle Swell (JFB)",
                    "recordOverall": {"wins": 8, "losses": 5},
                    "pointsFor": {"formatted": "1523.4"},
                    "pointsAgainst": {"formatted": "1401.2"},
                    "draftPosition": 10,
                    "owners": [{"displayName": "JoeDeGregorio"}],
                    "newItemCounts": {"activity": 86, "trades": 1},
                },
            ],
        },
        {
            "name": "Carter Football Conference",
            "teams": [
                {
                    "id": 200,
                    "name": "Some Other Team",
                    "recordOverall": {"wins": 3, "losses": 10},
                    "pointsFor": {"formatted": "900.1"},
                    "pointsAgainst": {"formatted": "1600.5"},
                },
            ],
        },
    ]
}


class TestParseRosterPlayers:
    def test_parses_valid_players(self):
        players = FleaflickerClient.parse_roster_players(SAMPLE_ROSTER)
        assert len(players) == 2
        assert players[0].name == "Patrick Mahomes"
        assert players[0].position == "QB"
        assert players[0].nfl_team == "KC"
        assert players[0].fleaflicker_id == "1001"
        assert players[1].name == "Derrick Henry"
        assert players[1].position == "RB"

    def test_empty_payload(self):
        assert FleaflickerClient.parse_roster_players({}) == []

    def test_skips_empty_slots(self):
        # The sample has 4 slots but only 2 valid players
        players = FleaflickerClient.parse_roster_players(SAMPLE_ROSTER)
        assert len(players) == 2


class TestParseTeamPicks:
    def test_parses_picks(self):
        picks = FleaflickerClient.parse_team_picks(SAMPLE_PICKS)
        assert len(picks) == 3
        assert picks[0].season == 2026
        assert picks[0].round == 1
        assert picks[0].slot == 5
        assert picks[0].original_owner == "Team Alpha"
        assert picks[0].current_owner == "Team Beta"
        assert picks[0].lost is False

    def test_lost_pick(self):
        picks = FleaflickerClient.parse_team_picks(SAMPLE_PICKS)
        assert picks[2].lost is True

    def test_empty_payload(self):
        assert FleaflickerClient.parse_team_picks({}) == []

    def test_missing_slot_field(self):
        picks = FleaflickerClient.parse_team_picks(SAMPLE_PICKS)
        assert picks[2].slot is None  # third pick has no "slot" in its slot dict


class TestParseStandings:
    def test_parses_teams(self):
        teams = FleaflickerClient.parse_standings(SAMPLE_STANDINGS_RICH)
        assert len(teams) == 2

    def test_basic_fields(self):
        teams = FleaflickerClient.parse_standings(SAMPLE_STANDINGS_RICH)
        t = teams[0]
        assert t.team_id == 100
        assert t.team_name == "Seattle Swell (JFB)"
        assert t.division == "Gow Football Conference"
        assert t.wins == 8
        assert t.losses == 5
        assert t.points_for == "1523.4"
        assert t.points_against == "1401.2"
        assert t.draft_position == 10

    def test_owner_names(self):
        teams = FleaflickerClient.parse_standings(SAMPLE_STANDINGS_RICH)
        assert teams[0].owner_display_names == ["JoeDeGregorio"]

    def test_activity_counts(self):
        teams = FleaflickerClient.parse_standings(SAMPLE_STANDINGS_RICH)
        assert teams[0].activity_unread == 86
        assert teams[0].trades_pending == 1

    def test_missing_optional_fields(self):
        teams = FleaflickerClient.parse_standings(SAMPLE_STANDINGS_RICH)
        t = teams[1]
        assert t.draft_position is None
        assert t.owner_display_names == []
        assert t.activity_unread == 0
        assert t.trades_pending == 0

    def test_empty_payload(self):
        assert FleaflickerClient.parse_standings({}) == []


class TestFindTeamStanding:
    def test_finds_existing_team(self):
        team = FleaflickerClient.find_team_standing(SAMPLE_STANDINGS, team_id=200)
        assert team["name"] == "Team Beta"

    def test_finds_team_in_second_division(self):
        team = FleaflickerClient.find_team_standing(SAMPLE_STANDINGS, team_id=300)
        assert team["name"] == "Team Gamma"

    def test_returns_empty_for_missing_team(self):
        assert FleaflickerClient.find_team_standing(SAMPLE_STANDINGS, team_id=999) == {}


class TestHTTPGet:
    @responses.activate
    def test_get_sends_correct_request(self):
        responses.add(
            responses.GET,
            f"{BASE_URL}/FetchLeagueStandings",
            json=SAMPLE_STANDINGS,
            status=200,
        )
        client = FleaflickerClient()
        result = client.get("FetchLeagueStandings", league_id=12345)
        assert result == SAMPLE_STANDINGS
        assert "league_id=12345" in responses.calls[0].request.url

    @responses.activate
    def test_fetch_standings_convenience(self):
        responses.add(
            responses.GET,
            f"{BASE_URL}/FetchLeagueStandings",
            json=SAMPLE_STANDINGS,
            status=200,
        )
        client = FleaflickerClient()
        result = client.fetch_standings(12345)
        assert result == SAMPLE_STANDINGS
