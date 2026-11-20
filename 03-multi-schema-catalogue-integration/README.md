# Multi-Schema Catalogue Integration

A synthetic-data project demonstrating how one canonical product catalogue can be transformed into three different downstream platform schemas.

## Why this project exists
Real catalogue integrations often receive inconsistent source fields, nested variants, warehouse-level inventory, missing attributes and different destination requirements. This project models those challenges without using any employer or client data.

## What it demonstrates
- Canonical data modelling independent of destination platforms
- Documented destination field-mapping specifications in JSON
- Explicit transformation functions for each destination contract
- Nested variant and warehouse inventory transformation
- Safe handling of missing and malformed fields
- Explicit validation issues rather than silently inventing values
- Three distinct destination payloads and a machine-readable quality report
- Automated tests with pytest

## Architecture
```text
data/raw/products.csv
        |
        v
Parse source fields and nested JSON
        |
        v
Canonical product model
        |
        +----> Schema A: flat commerce catalogue
        |
        +----> Schema B: nested commerce + warehouse inventory
        |
        +----> Schema C: discovery/search catalogue
        |
        v
Validation report (warnings and errors)
```

## Run locally (Windows PowerShell)
Python 3.11 or 3.12 is recommended.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.pipeline
pytest -q
```

## Outputs
Created in `data/processed/`:
- `schema_a.jsonl`
- `schema_b.jsonl`
- `schema_c.jsonl`
- `validation_report.json`

## Important data-integrity rule
Missing values are not automatically fabricated. The pipeline preserves nulls and reports missing required attributes. The synthetic sample includes a deliberately missing description and incomplete warehouse stock to exercise these cases. Any future demo-only enrichment must be explicitly labelled and kept separate from source facts.

All records are synthetic and independently created for this portfolio.
