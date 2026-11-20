# Large-Scale Catalogue Processing with PySpark

A reproducible local Spark project that generates synthetic product catalogue data, applies data-quality rules, calculates inventory metrics, and writes curated outputs.

## What it demonstrates
- Distributed DataFrame transformations with PySpark
- Explicit type casting and invalid-record filtering
- Derived metrics such as inventory value
- Sector- and category-level aggregations
- Parquet output for analytics workloads
- Automated tests with pytest

All data is synthetic. No employer, customer, or production data is included.

## Data flow
```text
generate_data.py
      |
      v
data/raw/products.csv
      |
      v
PySpark read + type casting
      |
      +----> rejected_records (invalid price / stock)
      |
      v
clean product records
      |
      +----> curated_products (Parquet)
      |
      +----> sector_summary (Parquet)
      |
      +----> category_summary (Parquet)
```

## Run locally (Windows PowerShell)
Use Python 3.11 and Java 17.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/generate_data.py
python src/pipeline.py
pytest -q
```

The pipeline runs Spark in local mode; it does not require a Spark cluster or cloud credentials.

## Outputs
Created under `data/processed/`:
- `curated_products/` — cleaned product records in Parquet
- `sector_summary/` — product count and inventory value by sector
- `category_summary/` — product count and average price by category
- `rejected_records/` — records rejected by quality rules

## Project structure
```text
02-pyspark-large-scale-processing/
├── data/
│   ├── raw/.gitkeep
│   └── processed/.gitkeep
├── src/
│   ├── generate_data.py
│   └── pipeline.py
├── tests/test_pipeline.py
├── requirements.txt
└── README.md
```

## Engineering notes
- The generator creates 10,000 deterministic synthetic records.
- Price and stock are cast explicitly before validation.
- Invalid records are retained separately for inspection rather than silently discarded.
- The pipeline is designed for local demonstration and can later be adapted to object storage and an orchestrator.
