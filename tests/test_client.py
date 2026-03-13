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
