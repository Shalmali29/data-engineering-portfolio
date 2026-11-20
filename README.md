# Data Engineering Portfolio

A practical portfolio of data engineering projects focused on reliable extraction, transformation, validation, and delivery of structured data.

**Data Engineer | Python · ETL · Data Pipelines · Data Quality**

## Projects

### 01 — Multilingual E-commerce Data Pipeline
A Python and pandas ETL pipeline that converts messy multilingual catalogue records into a canonical product dataset and configurable downstream platform schemas.

- Locale-aware price parsing (for example, `1.299,50` → `1299.50`)
- Availability normalization across English, German, French, and Spanish labels
- Duplicate detection and rejected-record reporting
- Configurable schema mappings for two downstream platforms
- Unit tests with pytest and GitHub Actions CI

[Open project documentation](./01-multilingual-ecommerce-pipeline/README.md)

### 02 — Large-Scale Catalogue Processing with PySpark
A local Spark ETL project that generates 10,000 synthetic catalogue records, validates them, separates rejected rows, and produces sector/category analytics in Parquet.

[Open project documentation](./02-pyspark-large-scale-processing/README.md)

### 03 — Multi-Schema Catalogue Integration
Transforms one canonical product model into three distinct destination payloads, including nested variants, warehouse inventory and validation reporting.

[Open project documentation](./03-multi-schema-catalogue-integration/README.md)

### 04 — Cloud Image and Asset Management Pipeline
Validates synthetic catalogue image assets, hashes files, stores them through local or optional Google Cloud Storage backends, and writes updated catalogue URLs with an error report.

[Open project documentation](./04-cloud-image-asset-pipeline/README.md)

### 05 — Real Estate Data Pipeline and RAG Search
Prepares synthetic property records for retrieval: validates catalogue data, creates structured search documents, supports local keyword retrieval, and provides optional sentence-transformer and Weaviate adapters.

[Open project documentation](./05-real-estate-rag-data-pipeline/README.md)

## Tech stack
Python, pandas, SQL, PySpark, PostgreSQL, GCP Cloud Storage, MongoDB, Weaviate, embeddings, data validation, ETL, web data extraction, GitHub Actions.

## About this portfolio
All datasets in this repository are synthetic and independently created for demonstration. No employer, customer, or production data is included.

More projects will be added here as separate, documented modules.
