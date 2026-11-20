# Multilingual E-commerce Data Pipeline

A portfolio ETL project that converts messy, multilingual product catalogue records into a clean canonical dataset and configurable platform-specific outputs.

## What it demonstrates
- Python ETL design with separate extraction, transformation, validation and loading stages
- Locale-aware price parsing (`1.299,50` → `1299.50`)
- Availability normalization across inconsistent source labels
- Missing-value, non-finite number and duplicate-ID handling
- Configurable schema mapping for downstream platforms
- Automated tests with `pytest`

All included records are synthetic and created for this portfolio project.

## Architecture

```text
data/raw/products.csv
        |
        v
   Extract (CSV)
        |
        v
 Transform + normalize
  - localized prices
  - availability
  - text / identifiers
        |
        v
  Data quality checks
        |
        v
 Canonical product schema
        |
        +----> platform_a.csv
        |
        +----> platform_b.csv
```

## Quick start (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.pipeline
pytest
```

Python 3.11 or 3.12 is recommended for broad package compatibility.

## Output

Running the pipeline creates:
- `data/processed/canonical_products.csv`
- `data/processed/platform_a_products.csv`
- `data/processed/platform_b_products.csv`
- `data/processed/rejected_records.csv`

## Project structure

```text
01-multilingual-ecommerce-pipeline/
├── config/schema_mappings.json
├── data/raw/products.csv
├── data/processed/.gitkeep
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   └── pipeline.py
├── tests/
│   ├── test_transform.py
│   └── test_validate.py
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Design notes
- Prices are represented as `Decimal` during parsing to avoid binary floating-point rounding errors.
- The pipeline retains rejected rows with a reason instead of silently dropping bad data.
- Canonical fields are independent of downstream platform field names.
- This first version uses CSV as a simple local source and sink. PostgreSQL and orchestration are planned as later extensions.

## Run tests

```powershell
pytest -q
```
