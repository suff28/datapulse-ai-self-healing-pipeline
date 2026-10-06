from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, Query, UploadFile
from sqlalchemy import text

from src.config import get_settings
from src.db import db_session
from src.generator import generate_orders
from src.pipeline import process_file, process_pending_files


app = FastAPI(title="DataPulse Pipeline API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate-sample")
def generate_sample(rows: int = Query(default=250, ge=10, le=5000)):
    output = Path(get_settings().data_incoming_dir) / "orders_messy_sample.csv"
    path = generate_orders(output, rows=rows, messy=True)
    return {"created": str(path), "rows": rows}


@app.post("/run")
def run_pipeline():
    return process_pending_files()


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    suffix = Path(file.filename or "upload.csv").suffix or ".csv"
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(await file.read())
        temp_path = Path(temp_file.name)
    result = process_file(temp_path)
    return result


@app.get("/runs")
def runs(limit: int = Query(default=20, ge=1, le=100)):
    with db_session() as connection:
        rows = connection.execute(
            text(
                """
                SELECT run_id, source_file, status, started_at, finished_at, total_rows,
                       clean_rows, quarantined_rows, quality_score, summary
                FROM pipeline_runs
                ORDER BY started_at DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
    return [dict(row) for row in rows]


@app.get("/quarantine")
def quarantine(limit: int = Query(default=50, ge=1, le=200)):
    with db_session() as connection:
        rows = connection.execute(
            text(
                """
                SELECT quarantine_id, run_id, source_file, row_number, raw_record, errors, repair_hint, created_at
                FROM quarantined_records
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
    return [dict(row) for row in rows]


@app.get("/quality")
def quality(limit: int = Query(default=50, ge=1, le=200)):
    with db_session() as connection:
        rows = connection.execute(
            text(
                """
                SELECT q.check_id, q.run_id, r.source_file, q.check_name, q.status, q.failed_rows, q.details, q.created_at
                FROM quality_checks q
                JOIN pipeline_runs r ON q.run_id = r.run_id
                ORDER BY q.created_at DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
    return [dict(row) for row in rows]


@app.get("/repair-suggestions")
def repair_suggestions(limit: int = Query(default=50, ge=1, le=200)):
    with db_session() as connection:
        rows = connection.execute(
            text(
                """
                SELECT suggestion_id, run_id, severity, issue_type, recommendation, example_fix, created_at
                FROM repair_suggestions
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
    return [dict(row) for row in rows]


@app.get("/metrics")
def metrics():
    with db_session() as connection:
        row = connection.execute(
            text(
                """
                SELECT
                    COUNT(*) AS total_runs,
                    COALESCE(SUM(total_rows), 0) AS total_rows,
                    COALESCE(SUM(clean_rows), 0) AS clean_rows,
                    COALESCE(SUM(quarantined_rows), 0) AS quarantined_rows,
                    COALESCE(ROUND(AVG(quality_score), 2), 0) AS avg_quality_score
                FROM pipeline_runs
                """
            )
        ).mappings().one()
    return dict(row)
