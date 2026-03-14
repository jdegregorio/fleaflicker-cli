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
fleaflicker standings --league-id 12345 --format normalized
```

### Team roster

```bash
fleaflicker roster --league-id 12345 --team-id 6789
fleaflicker roster --league-id 12345 --team-id 6789 --format table
fleaflicker roster --league-id 12345 --team-id 6789 --format normalized
```

### Draft picks

```bash
fleaflicker picks --league-id 12345 --team-id 6789
fleaflicker picks --league-id 12345 --team-id 6789 --format table
fleaflicker picks --league-id 12345 --team-id 6789 --format normalized
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

## Output Formats

| Format | Description |
|--------|-------------|
| `json` (default) | Raw API response |
| `table` | Human-readable Rich table |
| `normalized` | Parsed, flat JSON for downstream workflows |

### Normalized roster schema

```json
[
  {
    "name": "Justin Herbert",
    "position": "QB",
    "nfl_team": "LAC",
    "fleaflicker_id": "15516"
  }
]
```

### Normalized picks schema

```json
[
  {
    "season": 2026,
    "round": 1,
    "slot": 10,
    "original_owner": "Team Alpha",
    "current_owner": "Team Beta",
    "lost": true
  }
]
```

### Normalized standings schema

```json
[
  {
    "team_id": 1073671,
    "team_name": "Seattle Swell (JFB)",
    "division": "Gow Football Conference",
    "wins": 8,
    "losses": 5,
    "points_for": "1523.4",
    "points_against": "1401.2",
    "draft_position": 10,
    "owner_display_names": ["JoeDeGregorio"],
    "activity_unread": 86,
    "trades_pending": 1
  }
]
```

## Finding your IDs

Your league ID and team ID are visible in Fleaflicker URLs:

```
https://www.fleaflicker.com/nfl/leagues/12345/teams/6789
                                        ^^^^^       ^^^^
                                      league_id   team_id
```
