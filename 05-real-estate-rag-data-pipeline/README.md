# Real Estate Data Pipeline and RAG Search

A synthetic end-to-end data preparation and retrieval project inspired by property-catalogue search use cases. It ingests property records, validates and normalizes fields, creates searchable property documents, and supports local keyword retrieval. Optional modules add sentence-transformer embeddings and Weaviate vector storage.

All property records are synthetic. No customer, employer, or production data is included.

## Pipeline

```text
Synthetic property CSV
        |
        v
Validate + normalize records
        |
        v
Create clean property documents
        |
        +----------------------+
        |                      |
        v                      v
Local keyword retrieval   Optional embeddings
                               |
                               v
                         Weaviate vector DB
                               |
                               v
                       Semantic retrieval
```

## Quick start (Python 3.11+)

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -r requirements.txt
python -m src.pipeline
pytest -q
```

The default pipeline uses only the Python standard library and creates:
- `data/processed/properties_clean.csv`
- `data/processed/property_documents.jsonl`
- `data/processed/rejected_records.csv`

Run a local keyword query:

```bash
python -m src.search "family home near school"
```

## Optional semantic embeddings

Install the optional package:

```bash
python -m pip install -r requirements-embeddings.txt
```

The first run downloads the configured sentence-transformer model. Model downloads and inference are deliberately excluded from CI to keep tests small and deterministic.

## Optional Weaviate integration

Install the Weaviate client:

```bash
python -m pip install -r requirements-weaviate.txt
```

Configure a Weaviate instance and credentials through environment variables. Create a collection with a vectorizer set to `none` (bring-your-own-vectors), then use the integration module. Do not commit API keys or credentials.

```bash
export WEAVIATE_URL="https://your-instance.weaviate.network"
export WEAVIATE_API_KEY="your-api-key"
export WEAVIATE_COLLECTION="SyntheticProperty"
```

See `src/embeddings.py` and `src/weaviate_store.py` for the optional integration boundary. A real Weaviate deployment and model credentials are not included in this repository.

## Data quality rules
- Property ID is required and must be unique.
- Price and area must be positive numeric values.
- Bedrooms must be a non-negative integer.
- Required descriptive fields are trimmed and normalized.
- Invalid rows are retained in a separate rejection report with reasons.

## What this project demonstrates
Python ETL, data contracts, data quality, document preparation, keyword retrieval, optional vector embeddings, and a vector database integration boundary. The local keyword search is not presented as semantic search; semantic retrieval requires the optional embedding and Weaviate components.
