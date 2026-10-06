import json
import shutil
from pathlib import Path
from typing import Union
from uuid import uuid4

import pandas as pd
from sqlalchemy import text

from src.config import get_settings
from src.db import db_session
from src.normalizer import coerce_types, normalize_columns
from src.quality import compute_quality_score, flatten_issues, quality_checks, validate_orders
from src.repair_engine import build_repair_suggestions, explain_run


def process_file(file_path: Union[str, Path]) -> dict:
    settings = get_settings()
    source = Path(file_path)
    run_id = str(uuid4())

    raw_df = pd.read_csv(source)
    normalized_df, rename_map = normalize_columns(raw_df)
    typed_df = coerce_types(normalized_df)
    clean_df, quarantine, global_issues = validate_orders(typed_df)
    all_issues = flatten_issues(quarantine, global_issues)
    schema_failed = any(issue["issue_type"] == "missing_column" for issue in all_issues)
    score = compute_quality_score(len(raw_df), len(quarantine), schema_failed)
    summary = explain_run(len(raw_df), len(clean_df), len(quarantine), all_issues)
    checks = quality_checks(len(raw_df), len(clean_df), len(quarantine), all_issues)
    suggestions = build_repair_suggestions(all_issues)

    with db_session() as connection:
        _insert_run(connection, run_id, source.name, "completed", len(raw_df), len(clean_df), len(quarantine), score, summary)
        _insert_clean_orders(connection, run_id, source.name, clean_df)
        _insert_quarantine(connection, run_id, source.name, quarantine)
        _insert_quality_checks(connection, run_id, checks)
        _insert_suggestions(connection, run_id, suggestions)

    Path(settings.data_processed_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.data_quarantine_dir).mkdir(parents=True, exist_ok=True)
    clean_output = Path(settings.data_processed_dir) / f"{source.stem}_clean.csv"
    quarantine_output = Path(settings.data_quarantine_dir) / f"{source.stem}_quarantine.csv"
    clean_df.to_csv(clean_output, index=False)
    pd.DataFrame(quarantine).to_csv(quarantine_output, index=False)

    archive_path = source.with_suffix(source.suffix + ".processed")
    if source.exists() and not archive_path.exists():
        shutil.move(str(source), str(archive_path))

    return {
        "run_id": run_id,
        "source_file": source.name,
        "total_rows": len(raw_df),
        "clean_rows": len(clean_df),
        "quarantined_rows": len(quarantine),
        "quality_score": score,
        "column_mapping": rename_map,
        "summary": summary,
        "suggestions": suggestions,
    }


def process_pending_files() -> list[dict]:
    incoming = Path(get_settings().data_incoming_dir)
    incoming.mkdir(parents=True, exist_ok=True)
    results = []
    for file_path in sorted(incoming.glob("*.csv")):
        results.append(process_file(file_path))
    return results


def _insert_run(connection, run_id, source_file, status, total_rows, clean_rows, quarantined_rows, score, summary):
    connection.execute(
        text(
            """
            INSERT INTO pipeline_runs (
                run_id, source_file, status, finished_at, total_rows, clean_rows,
                quarantined_rows, quality_score, summary
            )
            VALUES (:run_id, :source_file, :status, NOW(), :total_rows, :clean_rows,
                    :quarantined_rows, :quality_score, :summary)
            """
        ),
        {
            "run_id": run_id,
            "source_file": source_file,
            "status": status,
            "total_rows": total_rows,
            "clean_rows": clean_rows,
            "quarantined_rows": quarantined_rows,
            "quality_score": score,
            "summary": summary,
        },
    )


def _insert_clean_orders(connection, run_id, source_file, df: pd.DataFrame):
    if df.empty:
        return
    records = []
    for record in df.to_dict(orient="records"):
        records.append(
            {
                "order_id": record["order_id"],
                "customer_id": record["customer_id"],
                "order_ts": record["order_ts"],
                "product_category": record["product_category"],
                "amount": float(record["amount"]),
                "quantity": int(record["quantity"]),
                "country": record["country"],
                "payment_method": record["payment_method"],
                "source_file": source_file,
                "run_id": run_id,
            }
        )
    connection.execute(
        text(
            """
            INSERT INTO clean_orders (
                order_id, customer_id, order_ts, product_category, amount, quantity,
                country, payment_method, source_file, run_id
            )
            VALUES (
                :order_id, :customer_id, :order_ts, :product_category, :amount,
                :quantity, :country, :payment_method, :source_file, :run_id
            )
            ON CONFLICT (order_id) DO NOTHING
            """
        ),
        records,
    )


def _insert_quarantine(connection, run_id, source_file, quarantine: list[dict]):
    if not quarantine:
        return
    records = []
    for item in quarantine:
        errors = item["errors"]
        records.append(
            {
                "run_id": run_id,
                "source_file": source_file,
                "row_number": item["row_number"],
                "raw_record": json.dumps(item["raw_record"]),
                "errors": json.dumps(errors),
                "repair_hint": errors[0]["message"] if errors else "Review quarantined record.",
            }
        )
    connection.execute(
        text(
            """
            INSERT INTO quarantined_records (run_id, source_file, row_number, raw_record, errors, repair_hint)
            VALUES (:run_id, :source_file, :row_number, CAST(:raw_record AS JSONB), CAST(:errors AS JSONB), :repair_hint)
            """
        ),
        records,
    )


def _insert_quality_checks(connection, run_id, checks: list[dict]):
    if not checks:
        return
    connection.execute(
        text(
            """
            INSERT INTO quality_checks (run_id, check_name, status, failed_rows, details)
            VALUES (:run_id, :check_name, :status, :failed_rows, :details)
            """
        ),
        [{**check, "run_id": run_id} for check in checks],
    )


def _insert_suggestions(connection, run_id, suggestions: list[dict]):
    if not suggestions:
        return
    connection.execute(
        text(
            """
            INSERT INTO repair_suggestions (run_id, severity, issue_type, recommendation, example_fix)
            VALUES (:run_id, :severity, :issue_type, :recommendation, :example_fix)
            """
        ),
        [{**suggestion, "run_id": run_id} for suggestion in suggestions],
    )


if __name__ == "__main__":
    print(process_pending_files())
