import json
from pathlib import Path
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from src.features import FEATURE_COLUMNS, build_pre_match_features

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "matches.csv"
OUT = ROOT / "data" / "processed"
LABELS = ["AWAY_WIN", "DRAW", "HOME_WIN"]

def validate_matches(frame: pd.DataFrame) -> pd.DataFrame:
    required = ["match_id", "match_date", "home_team", "away_team", "home_goals", "away_goals"]
    missing = set(required) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    data = frame.copy()
    data["match_date"] = pd.to_datetime(data["match_date"], errors="coerce")
    for col in ["home_goals", "away_goals"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    valid = (
        data["match_id"].notna() & data["match_date"].notna()
        & data["home_team"].notna() & data["away_team"].notna()
        & data["home_team"].ne(data["away_team"])
        & data["home_goals"].notna() & data["away_goals"].notna()
        & data["home_goals"].ge(0) & data["away_goals"].ge(0)
        & data["home_goals"].mod(1).eq(0) & data["away_goals"].mod(1).eq(0)
    )
    data = data.loc[valid].drop_duplicates(subset=["match_id"]).copy()
    if len(data) < 20:
        raise ValueError("At least 20 valid matches are required.")
    return data.sort_values(["match_date", "match_id"]).reset_index(drop=True)

def evaluate_models(features: pd.DataFrame):
    split = int(len(features) * 0.8)
    train, test = features.iloc[:split], features.iloc[split:]
    if train["target"].nunique() < 2 or test.empty:
        raise ValueError("Chronological split must contain multiple training classes and test rows.")
    X_train, X_test = train[FEATURE_COLUMNS], test[FEATURE_COLUMNS]
    y_train, y_test = train["target"], test["target"]
    models = {
        "majority_baseline": DummyClassifier(strategy="most_frequent"),
        "logistic_regression": make_pipeline(SimpleImputer(), StandardScaler(), LogisticRegression(max_iter=1000, random_state=42)),
        "random_forest": make_pipeline(SimpleImputer(), RandomForestClassifier(n_estimators=250, max_depth=8, min_samples_leaf=3, random_state=42, class_weight="balanced")),
    }
    metrics, predictions = {}, {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        p, r, f, _ = precision_recall_fscore_support(y_test, pred, average="weighted", zero_division=0)
        metrics[name] = {
            "accuracy": round(float(accuracy_score(y_test, pred)), 4),
            "precision_weighted": round(float(p), 4),
            "recall_weighted": round(float(r), 4),
            "f1_weighted": round(float(f), 4),
        }
        predictions[name] = pred
    selected = max(("logistic_regression", "random_forest"), key=lambda name: metrics[name]["f1_weighted"])
    result = pd.DataFrame({
        "match_id": test["match_id"].values,
        "match_date": test["match_date"].dt.strftime("%Y-%m-%d").values,
        "actual": y_test.values,
        "predicted": predictions[selected],
    })
    matrix = confusion_matrix(y_test, predictions[selected], labels=LABELS)
    return metrics, selected, result, pd.DataFrame(matrix, index=LABELS, columns=LABELS)

def run_pipeline(input_path=RAW, output_dir=OUT):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(input_path)
    clean = validate_matches(raw)
    engineered = build_pre_match_features(clean)
    metrics, selected, predictions, matrix = evaluate_models(engineered)
    engineered.to_csv(output_dir / "engineered_matches.csv", index=False)
    predictions.to_csv(output_dir / "test_predictions.csv", index=False)
    matrix.to_csv(output_dir / "confusion_matrix.csv")
    report = {"rows_received": int(len(raw)), "valid_rows": int(len(clean)), "rejected_rows": int(len(raw) - len(clean)), "train_rows": int(len(engineered) * 0.8), "test_rows": int(len(engineered) - int(len(engineered) * 0.8)), "selected_model": selected, "models": metrics}
    (output_dir / "model_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    run_pipeline()
