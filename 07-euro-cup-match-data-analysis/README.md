# Euro Cup Match Data Analysis & Prediction

A reproducible sports analytics project demonstrating match-data ingestion, validation, leakage-safe feature engineering, chronological model evaluation, and prediction reporting.

> **Data notice:** This project uses entirely synthetic football match data. It is an independent portfolio demonstration, not a reconstruction of official Euro Cup results or the original workplace dataset.

## Pipeline

1. Generate a deterministic synthetic match-results dataset.
2. Validate required fields, dates, teams, scores, and duplicate fixtures.
3. Build pre-match team-form features using only matches played before each fixture.
4. Split chronologically (earliest 80% for training, latest 20% for testing).
5. Compare a majority-class baseline, Logistic Regression, and Random Forest.
6. Write model metrics, test predictions, and a confusion matrix.

## Run locally

Python 3.11+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.generate_data
python -m src.pipeline
pytest -q
```

## Outputs

Generated under `data/processed/`:
- `engineered_matches.csv` — match rows with pre-match features
- `model_metrics.json` — accuracy, precision, recall, F1 and selected model
- `test_predictions.csv` — actual and predicted outcomes for the holdout period
- `confusion_matrix.csv` — class-level error summary

## Engineering decisions

- Features are calculated before the current match result is added to team history, preventing target leakage.
- The holdout set is later in time than the training set, reflecting forward-looking prediction.
- A simple baseline is included so model performance is not judged in isolation.
- Random seeds make data generation and model comparisons repeatable.
- Metrics are reported from the held-out test period; no accuracy claim is assumed in advance.

## Limitations

Synthetic data is useful for demonstrating an end-to-end workflow but cannot establish real-world tournament predictive performance. The project does not scrape external websites or use official competition data.
