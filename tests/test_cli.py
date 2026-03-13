"""Tests for CLI help text and basic invocation."""

from typer.testing import CliRunner

from fleaflicker_cli.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Fleaflicker" in result.output


def test_standings_help():
    result = runner.invoke(app, ["standings", "--help"])
    assert result.exit_code == 0
    assert "--league-id" in result.output


def test_roster_help():
    result = runner.invoke(app, ["roster", "--help"])
    assert result.exit_code == 0
    assert "--team-id" in result.output


def test_picks_help():
    result = runner.invoke(app, ["picks", "--help"])
    assert result.exit_code == 0
    assert "--team-id" in result.output


def test_raw_help():
    result = runner.invoke(app, ["raw", "--help"])
    assert result.exit_code == 0
    assert "ENDPOINT" in result.output


def test_roster_requires_team_id():
    result = runner.invoke(app, ["roster", "--league-id", "123"])
    assert result.exit_code == 1
