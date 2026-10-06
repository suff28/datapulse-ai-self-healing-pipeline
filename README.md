# DataPulse: AI Self-Healing Data Pipeline Platform

DataPulse is an end-to-end data engineering and AI reliability project that detects bad data before it breaks downstream analytics.

The platform ingests messy order data, normalizes source columns, validates schema and business rules, loads clean records into PostgreSQL, quarantines bad records, generates data quality checks, and produces AI-assisted repair suggestions for failed pipeline runs.

## Why This Project Matters

Real data pipelines fail because upstream systems change without warning:

- a column arrives as `price` instead of `amount`
- dates arrive in a bad format
- numeric fields contain strings
- required IDs are blank
- duplicate business keys appear
- unknown countries or payment methods enter the feed

DataPulse is built around that reality. It does not just load data. It checks, explains, quarantines, and suggests a fix.

## Architecture

```text
Messy CSV / Uploaded File / Generated Sample
        |
        v
Column Normalizer
        |
        v
Type Coercion + Data Quality Rules
        |
        +--> Clean records -> PostgreSQL clean_orders
        |
        +--> Failed records -> PostgreSQL quarantined_records
        |
        +--> Quality results -> PostgreSQL quality_checks
        |
        +--> Repair plans -> PostgreSQL repair_suggestions
        |
        v
FastAPI + Streamlit Dashboard
```

## Tech Stack

- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- FastAPI
- Streamlit
- Plotly
- Docker / Docker Compose
- Pytest

## Key Features

- Messy source data generator
- Column alias mapping
- Schema validation
- Type coercion
- Null checks
- Duplicate key detection
- Domain checks for country and payment method
- Bad record quarantine
- Data quality score
- AI-assisted repair suggestions
- FastAPI endpoints
- Streamlit monitoring dashboard
- Dockerized local deployment

## Quick Start: Local Demo

Run without Docker:

```bash
python3 demo_local.py
```

Outputs:

```text
sample_output/messy_orders.csv
sample_output/clean_orders.csv
sample_output/quarantined_records.csv
sample_output/datapulse_report.html
```

## Full Docker Run

```bash
cp .env.example .env
docker compose up --build
```

Open:

```text
API:       http://localhost:8010/docs
Dashboard: http://localhost:8510
```

In the dashboard:

1. Click **Generate Messy Data**
2. Click **Run Pipeline**
3. Review quality score, quarantined rows, checks, and repair suggestions

## API Endpoints

- `GET /health`
- `POST /generate-sample`
- `POST /run`
- `POST /upload`
- `GET /runs`
- `GET /quality`
- `GET /quarantine`
- `GET /repair-suggestions`
- `GET /metrics`

## Interview Explanation

> I built DataPulse, an AI self-healing data pipeline platform. It ingests messy order data, normalizes inconsistent source columns, validates schema and business rules, loads clean records into PostgreSQL, quarantines bad records, and generates repair suggestions for pipeline failures. The goal was to model what happens in real data engineering work: upstream data changes, pipelines fail, and engineers need observability, quarantine handling, and clear recovery steps.

## Resume Bullets

- Built DataPulse, an AI-assisted data quality platform using Python, Pandas, PostgreSQL, FastAPI, Streamlit, and Docker to validate, clean, quarantine, and monitor messy source data.
- Designed a self-healing pipeline that maps source column aliases, coerces data types, validates business rules, stores clean records, and routes failed records to quarantine with repair hints.
- Implemented data quality checks for missing fields, type errors, invalid dates, duplicate keys, invalid domains, and range violations, with run-level quality scoring.
- Created API and dashboard layers to monitor pipeline runs, failed records, quality checks, and AI-assisted repair recommendations.

## Project Structure

```text
datapulse-ai-data-pipeline/
  dashboard/
  data/
  docs/
  sample_output/
  sql/
  src/
  tests/
  docker-compose.yml
  Dockerfile
  Makefile
  README.md
```
