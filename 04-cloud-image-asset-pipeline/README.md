# Cloud Image and Asset Management Pipeline

A safe, reproducible demonstration of catalogue image asset handling. It validates local image files, calculates content hashes, copies assets into deterministic storage paths, generates stable URLs, and writes an updated catalogue plus an error report.

All sample records and image files are synthetic. No employer or customer assets are included.

## What it demonstrates
- Image file existence and extension validation
- SHA-256 content hashing and deterministic object names
- Local storage adapter for zero-credential execution
- Optional Google Cloud Storage adapter
- Catalogue URL replacement and rejected-record reporting
- Automated tests with pytest

## Architecture
```text
Synthetic catalogue CSV + local image assets
                 |
                 v
          Validate image file
                 |
                 v
       SHA-256 + deterministic key
                 |
          +------+------+
          |             |
          v             v
     Local storage   GCS bucket
          |             |
          +------+------+
                 |
                 v
      Updated catalogue CSV
       + asset error report
```

## Run locally (Windows PowerShell)
Python 3.11 or 3.12 is recommended.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.generate_sample_data
python -m src.pipeline
pytest -q
```

By default, the project uses local storage and requires no cloud account. Output is written to `data/processed/`.

## Optional Google Cloud Storage mode
Install the optional dependency:

```powershell
python -m pip install "google-cloud-storage>=2.18,<4"
```

Set environment variables in your terminal (never commit credentials):

```powershell
$env:ASSET_STORAGE_BACKEND = "gcs"
$env:GCS_BUCKET = "your-test-bucket"
$env:GCS_PREFIX = "portfolio/catalogue-assets"
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\secure-path\service-account.json"
python -m src.pipeline
```

The service account should have only the permissions required to create objects in the test bucket. The pipeline does not make objects public. By default it records `gs://bucket/object` URIs. If a CDN or public base URL is configured with `ASSET_PUBLIC_BASE_URL`, it emits that URL plus the object key; configure that base URL only when the bucket/CDN is actually serving the objects.

## Input and output
Input CSV: `data/raw/catalogue.csv`. Image paths must resolve inside `data/raw/assets/`.

Outputs:
- `data/processed/catalogue_with_asset_urls.csv`
- `data/processed/asset_errors.csv`
- Local copied assets under `data/processed/assets/` (local backend only)

## Security and reliability notes
- The demo accepts local asset paths rather than downloading arbitrary URLs.
- Path traversal outside the supplied asset directory is rejected.
- SHA-256 object keys make repeated uploads deterministic.
- GCS credentials are supplied through Application Default Credentials or the environment; secrets are not stored in the repository.
- This is a portfolio-scale reference implementation, not a claim of production deployment.
