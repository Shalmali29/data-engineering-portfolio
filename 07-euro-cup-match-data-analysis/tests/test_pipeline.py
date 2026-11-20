import pandas as pd
import pytest
from src.features import FEATURE_COLUMNS, build_pre_match_features
from src.pipeline import validate_matches, evaluate_models

def sample_matches():
    rows = []
    teams = ["A", "B", "C", "D"]
    for i in range(80):
        rows.append({
            "match_id": f"M{i}", "match_date": (pd.Timestamp("2024-01-01") + pd.Timedelta(days=i)).date().isoformat(),
            "home_team": teams[i % 4], "away_team": teams[(i + 1) % 4],
            "home_goals": (i * 3) % 4, "away_goals": (i * 5 + 1) % 3,
        })
    return pd.DataFrame(rows)

def test_validation_removes_bad_and_duplicate_rows():
    raw = sample_matches()
    raw.loc[0, "home_goals"] = -1
    raw.loc[1, "match_id"] = raw.loc[2, "match_id"]
    clean = validate_matches(raw)
    assert len(clean) == len(raw) - 2

def test_pre_match_features_do_not_use_current_match_result():
    raw = sample_matches().iloc[:8].copy()
    first = build_pre_match_features(raw)
    changed = raw.copy()
    changed.loc[0, "home_goals"] = 99
    second = build_pre_match_features(changed)
    assert first.loc[0, FEATURE_COLUMNS].equals(second.loc[0, FEATURE_COLUMNS])

def test_feature_builder_creates_target_and_feature_columns():
    engineered = build_pre_match_features(sample_matches())
    assert set(FEATURE_COLUMNS).issubset(engineered.columns)
    assert set(engineered["target"]).issubset({"HOME_WIN", "DRAW", "AWAY_WIN"})

def test_chronological_evaluation_returns_metrics_and_predictions():
    engineered = build_pre_match_features(sample_matches())
    metrics, selected, predictions, matrix = evaluate_models(engineered)
    assert selected in {"logistic_regression", "random_forest"}
    assert set(metrics) == {"majority_baseline", "logistic_regression", "random_forest"}
    assert len(predictions) == 16
    assert matrix.shape == (3, 3)
