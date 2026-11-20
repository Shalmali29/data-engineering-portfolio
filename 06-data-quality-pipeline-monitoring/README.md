# Data Quality and Pipeline Monitoring

A synthetic data quality monitoring project that profiles incoming catalogue batches, applies reusable validation rules, records row-level failures, and produces a run-level monitoring report.

All data is synthetic and independently created for this portfolio.

## What it demonstrates
- Reusable data quality rules: required fields, uniqueness, numeric ranges, accepted values
- Row-level quarantine with clear failure reasons
- Batch-level metrics and quality score
- Run status (SUCCESS, WARNING, FAILED) based on configurable thresholds
- JSON monitoring report and CSV quarantine output
- Deterministic unit tests

## Quick start (Python 3.11+)
```bash
python -m venv .venv
# Activate environment, then:
python -m pip install -r requirements.txt
python -m src.generate_sample_data
python -m src.monitor
pytest -q
```

Outputs are written to `data/processed/`:
- `accepted_records.csv`: records passing all checks
- `quarantined_records.csv`: rejected records and validation reasons
- `quality_report.json`: batch-level metrics and rule counts

## Quality score and status
The quality score is the percentage of input records accepted. Status is evaluated using `--warning-threshold` and `--failure-threshold`:
- SUCCESS: score meets or exceeds the warning threshold
- WARNING: score is below warning but meets failure threshold
- FAILED: score is below failure threshold

Defaults are 95% and 80%, respectively. Empty input is FAILED.

## Example
```bash
python -m src.monitor --warning-threshold 95 --failure-threshold 80
```

This is a batch-level monitoring reference implementation. It does not claim to integrate with a production alerting service or orchestration platform.
