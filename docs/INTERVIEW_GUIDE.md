# Interview Guide

## 30-Second Explanation

DataPulse is a self-healing data pipeline platform. It takes messy order data, normalizes source columns, validates schema and business rules, stores clean records in PostgreSQL, quarantines bad records, and generates repair suggestions so the pipeline failure is explainable.

## Why I Built It

In real data engineering, pipelines often fail because upstream data changes. A column name changes, a date format breaks, duplicate IDs appear, or required fields are missing. I wanted to build a project that shows how to handle those failures properly instead of just loading a CSV.

## What Happens Step by Step

1. A CSV file arrives.
2. The pipeline maps source columns to the expected contract.
3. It coerces values into expected types.
4. It validates each row.
5. Clean rows go into `clean_orders`.
6. Bad rows go into `quarantined_records`.
7. Quality checks and run metrics are stored.
8. Repair suggestions explain what went wrong and how to fix it.
9. FastAPI and Streamlit expose the results.

## Things To Say In An Interview

- I treated data quality as part of the pipeline, not an afterthought.
- I separated clean records from quarantined records so bad data does not block all good data.
- I used a data contract so the pipeline knows what it expects.
- I created repair suggestions from grouped failure patterns.
- I containerized the system with Docker Compose so it can run consistently.

## Technical Questions

### Why quarantine instead of dropping bad rows?

Dropping rows hides data quality problems. Quarantine keeps bad records available for review and gives the data team a way to fix source issues.

### Why use a quality score?

A quality score makes pipeline health easy to compare across runs. It helps identify whether data is improving or degrading.

### Why PostgreSQL?

PostgreSQL is reliable for structured pipeline metadata, clean records, quarantined records, and operational reporting.

### Is this really AI?

The project uses an AI-assisted repair layer based on issue classification and deterministic recommendations. It is intentionally auditable. In production, this could be extended with an LLM to generate richer explanations, but the core logic should remain rule-backed and reliable.
