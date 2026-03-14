"""Typer CLI for the Fleaflicker fantasy football API."""

import json
from dataclasses import asdict
from enum import StrEnum
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from fleaflicker_cli.client import FleaflickerClient

app = typer.Typer(
    name="fleaflicker",
    help="CLI for the Fleaflicker fantasy football API.",
    no_args_is_help=True,
)
console = Console()

LEAGUE_ID_OPT = typer.Option("--league-id", help="Fleaflicker league ID")
TEAM_ID_OPT = typer.Option("--team-id", help="Fleaflicker team ID")
FORMAT_OPT = typer.Option("--format", help="Output format")


class OutputFormat(StrEnum):
    json = "json"
    table = "table"
    normalized = "normalized"


def _print_json(data) -> None:
    """Pretty-print any JSON-serialisable object."""
    console.print_json(json.dumps(data, default=str))


def _require_team_id(team_id: int | None) -> int:
    if team_id is None:
        console.print(
            "[red]Error:[/red] --team-id is required for this command."
        )
        raise typer.Exit(code=1)
    return team_id


# ── Commands ─────────────────────────────────────────────────


@app.command()
def standings(
    league_id: Annotated[int, LEAGUE_ID_OPT],
    fmt: Annotated[OutputFormat, FORMAT_OPT] = OutputFormat.json,
) -> None:
    """Fetch and display league standings."""
    client = FleaflickerClient()
    data = client.fetch_standings(league_id)

    if fmt == OutputFormat.normalized:
        teams = client.parse_standings(data)
        _print_json([asdict(t) for t in teams])
    elif fmt == OutputFormat.table:
        table = Table(title="League Standings")
        table.add_column("Division", style="bold")
        table.add_column("Team")
        table.add_column("W", justify="right")
        table.add_column("L", justify="right")
        table.add_column("PF", justify="right")
        for division in data.get("divisions", []):
            div_name = division.get("name", "")
            for team in division.get("teams", []):
                record = team.get("recordOverall", {})
                pf = team.get("pointsFor", {}).get(
                    "formatted", ""
                )
                table.add_row(
                    div_name,
                    team.get("name", ""),
                    str(record.get("wins", 0)),
                    str(record.get("losses", 0)),
                    pf,
                )
        console.print(table)
    else:
        _print_json(data)


@app.command()
def roster(
    league_id: Annotated[int, LEAGUE_ID_OPT],
    team_id: Annotated[int | None, TEAM_ID_OPT] = None,
    fmt: Annotated[OutputFormat, FORMAT_OPT] = OutputFormat.json,
) -> None:
    """Fetch and display a team roster."""
    tid = _require_team_id(team_id)
    client = FleaflickerClient()
    data = client.fetch_roster(league_id, tid)

    if fmt == OutputFormat.normalized:
        players = client.parse_roster_players(data)
        _print_json([asdict(p) for p in players])
    elif fmt == OutputFormat.table:
        players = client.parse_roster_players(data)
        table = Table(title="Team Roster")
        table.add_column("Name")
        table.add_column("Pos")
        table.add_column("NFL Team")
        table.add_column("ID", justify="right")
        for p in players:
            table.add_row(
                p.name,
                p.position,
                p.nfl_team or "",
                p.fleaflicker_id or "",
            )
        console.print(table)
    else:
        _print_json(data)


@app.command()
def picks(
    league_id: Annotated[int, LEAGUE_ID_OPT],
    team_id: Annotated[int | None, TEAM_ID_OPT] = None,
    fmt: Annotated[OutputFormat, FORMAT_OPT] = OutputFormat.json,
) -> None:
    """Fetch and display draft picks for a team."""
    tid = _require_team_id(team_id)
    client = FleaflickerClient()
    data = client.fetch_team_picks(league_id, tid)

    if fmt == OutputFormat.normalized:
        draft_picks = client.parse_team_picks(data)
        _print_json([asdict(dp) for dp in draft_picks])
    elif fmt == OutputFormat.table:
        draft_picks = client.parse_team_picks(data)
        table = Table(title="Draft Picks")
        table.add_column("Season", justify="right")
        table.add_column("Round", justify="right")
        table.add_column("Slot", justify="right")
        table.add_column("Original Owner")
        table.add_column("Current Owner")
        table.add_column("Lost")
        for dp in draft_picks:
            table.add_row(
                str(dp.season),
                str(dp.round),
                str(dp.slot) if dp.slot is not None else "",
                dp.original_owner,
                dp.current_owner,
                "Yes" if dp.lost else "",
            )
        console.print(table)
    else:
        _print_json(data)


@app.command()
def rosters(
    league_id: Annotated[int, LEAGUE_ID_OPT],
    fmt: Annotated[OutputFormat, FORMAT_OPT] = OutputFormat.json,
) -> None:
    """Fetch all league rosters."""
    client = FleaflickerClient()
    data = client.fetch_league_rosters(league_id)

    if fmt == OutputFormat.table:
        table = Table(title="League Rosters")
        table.add_column("Team")
        table.add_column("Player")
        table.add_column("Pos")
        table.add_column("NFL Team")
        for team in data.get("rosters", []):
            team_name = team.get("team", {}).get("name", "")
            for player_entry in team.get("players", []):
                pro = player_entry.get("proPlayer", {})
                table.add_row(
                    team_name,
                    pro.get("nameFull", ""),
                    pro.get("position", ""),
                    pro.get("proTeamAbbreviation", ""),
                )
        console.print(table)
    else:
        _print_json(data)


@app.command()
def raw(
    endpoint: Annotated[
        str, typer.Argument(help="Fleaflicker API endpoint name")
    ],
    league_id: Annotated[int, LEAGUE_ID_OPT],
    team_id: Annotated[int | None, TEAM_ID_OPT] = None,
) -> None:
    """Make a raw API call and output the JSON response."""
    client = FleaflickerClient()
    params: dict = {"league_id": league_id}
    if team_id is not None:
        params["team_id"] = team_id
    data = client.get(endpoint, **params)
    _print_json(data)
