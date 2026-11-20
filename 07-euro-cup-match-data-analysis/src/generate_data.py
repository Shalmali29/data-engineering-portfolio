from pathlib import Path
import random
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "matches.csv"

def generate_matches(n_matches: int = 480, seed: int = 2024) -> pd.DataFrame:
    rng = random.Random(seed)
    teams = {
        "Northport": 1.35, "Westhaven": 1.20, "Eastford": 1.10,
        "Southbridge": 1.00, "Rivermouth": 0.95, "Hillchester": 0.90,
        "Kingsvale": 0.85, "Lakewood": 0.80, "Fairview": 0.75,
        "Ashford": 0.70, "Stonefield": 0.65, "Brookside": 0.60,
    }
    names = list(teams)
    rows = []
    for idx in range(n_matches):
        home, away = rng.sample(names, 2)
        home_rate = teams[home] * 1.10
        away_rate = teams[away]
        home_goals = min(6, max(0, int(rng.expovariate(1 / home_rate))))
        away_goals = min(6, max(0, int(rng.expovariate(1 / away_rate))))
        rows.append({
            "match_id": f"M{idx + 1:04d}",
            "match_date": (pd.Timestamp("2022-01-01") + pd.Timedelta(days=idx * 2)).date().isoformat(),
            "home_team": home,
            "away_team": away,
            "home_goals": home_goals,
            "away_goals": away_goals,
        })
    return pd.DataFrame(rows)

def main() -> None:
    RAW.parent.mkdir(parents=True, exist_ok=True)
    generate_matches().to_csv(RAW, index=False)
    print(f"Wrote synthetic matches to {RAW}")

if __name__ == "__main__":
    main()
