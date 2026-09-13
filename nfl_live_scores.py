import time
import requests
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.console import Group

def get_live_nfl_scores():
    # Hit ESPN's public scoreboard endpoint
    url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    response = requests.get(url)

    # Signal a rate limit hit back to the caller
    if response.status_code == 429:
        return None

    data = response.json()
    games = data.get("events", [])
    results = []

    for game in games:
        competitions = game["competitions"][0]
        state = competitions["status"]["type"]["state"]

        # Only keep games that are currently in progress
        if state != "in":
            continue

        status = competitions["status"]["type"]["shortDetail"]
        teams = competitions["competitors"]

        home = next(t for t in teams if t["homeAway"] == "home")
        away = next(t for t in teams if t["homeAway"] == "away")

        results.append({
            "home_team": home["team"]["displayName"],
            "home_score": home.get("score", "0"),
            "away_team": away["team"]["displayName"],
            "away_score": away.get("score", "0"),
            "status": status
        })

    return results

def build_table(scores):
    # Rebuild the table fresh each refresh
    table = Table()

    table.add_column("Away")
    table.add_column("Score", justify="center")
    table.add_column("Home")
    table.add_column("Score", justify="center")
    table.add_column("Status")

    for game in scores:
        table.add_row(
            game["away_team"],
            game["away_score"],
            game["home_team"],
            game["home_score"],
            game["status"]
        )

    return table

def build_display(scores, seconds_left):
    # Combine the scores table with the countdown text
    table = build_table(scores)
    countdown = f"Next update in {seconds_left} seconds"
    return Group(table, countdown)

def run():
    console = Console()
    interval = 30
    backoff = interval
    scores = []

    with Live(console=console, refresh_per_second=1) as live:
        while True:
            result = get_live_nfl_scores()

            if result is None:
                # Back off exponentially if we're getting rate limited
                backoff = min(backoff * 2, 300)
                wait = backoff
            else:
                scores = result
                backoff = interval
                wait = interval

            # Count down one second at a time, updating the display each tick
            for remaining in range(wait, 0, -1):
                live.update(build_display(scores, remaining))
                time.sleep(1)

run()
