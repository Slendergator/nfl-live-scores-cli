import time
import requests
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.console import Group
from rich.text import Text
from datetime import datetime

def get_live_nfl_scores():
    url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    response = requests.get(url)

    if response.status_code == 429:
        return None

    data = response.json()
    games = data.get("events", [])
    results = []

    for game in games:
        competitions = game["competitions"][0]
        state = competitions["status"]["type"]["state"]

        if state != "in":
            continue

        status = competitions["status"]["type"]["shortDetail"]
        teams = competitions["competitors"]

        home = next(t for t in teams if t["homeAway"] == "home")
        away = next(t for t in teams if t["homeAway"] == "away")

        results.append({
            "id": game["id"],
            "home_team": home["team"]["displayName"],
            "home_score": home.get("score", "0"),
            "away_team": away["team"]["displayName"],
            "away_score": away.get("score", "0"),
            "status": status
        })

    return results

def update_change_tracker(scores, last_scores, last_changed, log):
    now = time.time()
    timestamp = datetime.now().strftime("%H:%M:%S")

    for game in scores:
        gid = game["id"]
        prev = last_scores.get(gid)

        if prev is None:
            last_changed[gid] = {"home": 0, "away": 0}
        else:
            if game["home_score"] != prev["home_score"]:
                last_changed.setdefault(gid, {"home": 0, "away": 0})
                last_changed[gid]["home"] = now
                log.append(f"{timestamp} {game['home_team']} {prev['home_score']} -> {game['home_score']}")

            if game["away_score"] != prev["away_score"]:
                last_changed.setdefault(gid, {"home": 0, "away": 0})
                last_changed[gid]["away"] = now
                log.append(f"{timestamp} {game['away_team']} {prev['away_score']} -> {game['away_score']}")

        last_scores[gid] = game

def build_table(scores, last_changed):
    table = Table()

    table.add_column("Away")
    table.add_column("Score", justify="center")
    table.add_column("Home")
    table.add_column("Score", justify="center")
    table.add_column("Status")

    now = time.time()

    for game in scores:
        gid = game["id"]
        changed = last_changed.get(gid, {"home": 0, "away": 0})

        away_score = game["away_score"]
        home_score = game["home_score"]

        if now - changed["away"] < 30:
            away_score = f"[green]{away_score}[/green]"

        if now - changed["home"] < 30:
            home_score = f"[green]{home_score}[/green]"

        table.add_row(
            game["away_team"],
            away_score,
            game["home_team"],
            home_score,
            game["status"]
        )

    return table

def build_log_panel(log):
    if not log:
        return Text("No scoring events yet", style="dim")

    lines = log[-15:]
    return Text("\n".join(lines))

def build_display(scores, last_changed, seconds_left, log):
    table = build_table(scores, last_changed)
    countdown = f"Next update in {seconds_left} seconds"
    log_panel = build_log_panel(log)
    return Group(table, countdown, "", "Scoring Log:", log_panel)

def run():
    console = Console()
    interval = 60
    backoff = interval
    scores = []
    last_scores = {}
    last_changed = {}
    log = []

    with Live(console=console, refresh_per_second=1) as live:
        while True:
            result = get_live_nfl_scores()

            if result is None:
                backoff = min(backoff * 2, 300)
                wait = backoff
            else:
                update_change_tracker(result, last_scores, last_changed, log)
                scores = result
                backoff = interval
                wait = interval

            for remaining in range(wait, 0, -1):
                live.update(build_display(scores, last_changed, remaining, log))
                time.sleep(1)

run()
