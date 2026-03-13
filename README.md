# fleaflicker-cli

A command-line interface for the [Fleaflicker](https://www.fleaflicker.com/) fantasy football API.

## Installation

```bash
pip install .
```

For development:

```bash
pip install -e ".[dev]"
# or
pip install -e . && pip install pytest ruff responses
```

## Usage

Every command requires `--league-id`. Commands that target a specific team also require `--team-id`.

### League standings

```bash
fleaflicker standings --league-id 12345
fleaflicker standings --league-id 12345 --format table
```

### Team roster

```bash
fleaflicker roster --league-id 12345 --team-id 6789
fleaflicker roster --league-id 12345 --team-id 6789 --format table
```

### Draft picks

```bash
fleaflicker picks --league-id 12345 --team-id 6789
fleaflicker picks --league-id 12345 --team-id 6789 --format table
```

### All league rosters

```bash
fleaflicker rosters --league-id 12345
```

### Raw API call

```bash
fleaflicker raw FetchLeagueStandings --league-id 12345
fleaflicker raw FetchRoster --league-id 12345 --team-id 6789
```

## Output

All commands output JSON by default. Pass `--format table` for a human-readable Rich table.

## Finding your IDs

Your league ID and team ID are visible in Fleaflicker URLs:

```
https://www.fleaflicker.com/nfl/leagues/12345/teams/6789
                                        ^^^^^       ^^^^
                                      league_id   team_id
```
