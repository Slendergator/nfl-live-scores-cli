# nfl-live-scores-cli

Live NFL scores in your terminal, powered by ESPN's public API. Auto-refreshes every minute with a countdown timer, showing only in-progress games.

## Features

- Pulls live NFL scores from ESPN's public scoreboard endpoint
- Filters out games that haven't started or are already final
- Displays scores in a clean terminal table
- Highlights a score in green for 30 seconds after it changes
- Keeps a running log of scoring events below the table
- Countdown timer shows time until the next refresh
- Automatic backoff if rate limited

## Requirements

- Python 3.7+
- `requests`
- `rich`

## Installation

```bash
pip install requests rich
```

## Usage

```bash
python nfl_live_scores.py
```

The table will refresh every minute with a live countdown. Recently changed scores show in green, and the scoring log underneath tracks each change with a timestamp. Press `Ctrl+C` to exit.

## Notes

This project uses an unofficial, undocumented ESPN API endpoint. It could change or stop working without notice. Be respectful of request frequency to avoid being rate limited.

## License

I don't fucking care lol
