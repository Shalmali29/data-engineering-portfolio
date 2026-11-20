import pandas as pd

FEATURE_COLUMNS = [
    "home_scored_avg", "home_conceded_avg", "home_points_avg",
    "away_scored_avg", "away_conceded_avg", "away_points_avg",
]

def build_pre_match_features(matches: pd.DataFrame) -> pd.DataFrame:
    required = {"match_date", "home_team", "away_team", "home_goals", "away_goals"}
    missing = required - set(matches.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    frame = matches.copy()
    frame["match_date"] = pd.to_datetime(frame["match_date"], errors="raise")
    frame = frame.sort_values(["match_date"], kind="stable").reset_index(drop=True)
    history = {}
    output = []

    def averages(team):
        games = history.get(team, [])
        if not games:
            return (1.2, 1.2, 1.0)
        recent = games[-5:]
        count = len(recent)
        return (
            sum(g[0] for g in recent) / count,
            sum(g[1] for g in recent) / count,
            sum(g[2] for g in recent) / count,
        )

    for row in frame.itertuples(index=False):
        home = row.home_team
        away = row.away_team
        h = averages(home)
        a = averages(away)
        result = "DRAW" if row.home_goals == row.away_goals else ("HOME_WIN" if row.home_goals > row.away_goals else "AWAY_WIN")
        output.append({
            **row._asdict(),
            "home_scored_avg": h[0], "home_conceded_avg": h[1], "home_points_avg": h[2],
            "away_scored_avg": a[0], "away_conceded_avg": a[1], "away_points_avg": a[2],
            "target": result,
        })
        home_points = 3 if result == "HOME_WIN" else (1 if result == "DRAW" else 0)
        away_points = 3 if result == "AWAY_WIN" else (1 if result == "DRAW" else 0)
        history.setdefault(home, []).append((row.home_goals, row.away_goals, home_points))
        history.setdefault(away, []).append((row.away_goals, row.home_goals, away_points))

    return pd.DataFrame(output)
