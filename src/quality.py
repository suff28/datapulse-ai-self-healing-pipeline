from collections import Counter
import pandas as pd

from src.contracts import EXPECTED_COLUMNS, VALID_COUNTRIES, VALID_PAYMENT_METHODS, ValidationIssue


def validate_orders(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict], list[dict]]:
    issues: list[ValidationIssue] = []

    missing_columns = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    for column in missing_columns:
        issues.append(
            ValidationIssue(
                row_number=0,
                field=column,
                issue_type="missing_column",
                message=f"Required column '{column}' is missing from the source file.",
                severity="high",
            )
        )

    if missing_columns:
        return df.iloc[0:0].copy(), [], [_issue_to_dict(issue) for issue in issues]

    row_errors: dict[int, list[ValidationIssue]] = {}

    for idx, row in df.iterrows():
        row_number = int(idx) + 2
        checks = [
            _required(row, row_number, "order_id"),
            _required(row, row_number, "customer_id"),
            _required(row, row_number, "product_category"),
            _positive_amount(row, row_number),
            _positive_quantity(row, row_number),
            _valid_timestamp(row, row_number),
            _valid_country(row, row_number),
            _valid_payment(row, row_number),
        ]
        for issue in [check for check in checks if check is not None]:
            row_errors.setdefault(idx, []).append(issue)

    duplicate_mask = df["order_id"].duplicated(keep="first")
    for idx in df[duplicate_mask].index:
        row_errors.setdefault(idx, []).append(
            ValidationIssue(
                row_number=int(idx) + 2,
                field="order_id",
                issue_type="duplicate_key",
                message="Duplicate order_id found. Keeping only the first clean record.",
                severity="high",
            )
        )

    clean_df = df.drop(index=list(row_errors.keys())).copy()
    quarantine = []
    for idx, errors in row_errors.items():
        quarantine.append(
            {
                "row_number": int(idx) + 2,
                "raw_record": _json_safe_record(df.loc[idx].to_dict()),
                "errors": [_issue_to_dict(error) for error in errors],
            }
        )
    return clean_df, quarantine, [_issue_to_dict(issue) for issue in issues]


def quality_checks(total_rows: int, clean_rows: int, quarantine_rows: int, issues: list[dict]) -> list[dict]:
    fail_rate = 0 if total_rows == 0 else quarantine_rows / total_rows
    issue_counts = Counter(issue["issue_type"] for issue in issues)
    checks = [
        {
            "check_name": "schema_contract",
            "status": "failed" if issue_counts.get("missing_column") else "passed",
            "failed_rows": issue_counts.get("missing_column", 0),
            "details": "Source file must contain all required business columns.",
        },
        {
            "check_name": "record_validity",
            "status": "failed" if quarantine_rows else "passed",
            "failed_rows": quarantine_rows,
            "details": "Rows with null keys, bad dates, invalid payments, or bad amounts are quarantined.",
        },
        {
            "check_name": "quality_score",
            "status": "failed" if fail_rate > 0.20 else "passed",
            "failed_rows": quarantine_rows,
            "details": f"Clean rows: {clean_rows}; quarantined rows: {quarantine_rows}; total rows: {total_rows}.",
        },
    ]
    return checks


def compute_quality_score(total_rows: int, quarantined_rows: int, schema_failed: bool) -> float:
    if total_rows == 0:
        return 0.0
    score = 100 * (1 - quarantined_rows / total_rows)
    if schema_failed:
        score -= 30
    return round(max(score, 0), 2)


def flatten_issues(quarantine: list[dict], global_issues: list[dict]) -> list[dict]:
    issues = list(global_issues)
    for record in quarantine:
        issues.extend(record["errors"])
    return issues


def _required(row: pd.Series, row_number: int, field: str):
    value = row[field]
    if pd.isna(value) or str(value).strip() == "":
        return ValidationIssue(row_number, field, "missing_value", f"{field} is required.", "high")
    return None


def _positive_amount(row: pd.Series, row_number: int):
    value = row["amount"]
    if pd.isna(value):
        return ValidationIssue(row_number, "amount", "type_error", "amount must be numeric.", "high")
    if float(value) <= 0:
        return ValidationIssue(row_number, "amount", "range_error", "amount must be greater than 0.", "high")
    return None


def _positive_quantity(row: pd.Series, row_number: int):
    value = row["quantity"]
    if pd.isna(value):
        return ValidationIssue(row_number, "quantity", "type_error", "quantity must be an integer.", "high")
    if int(value) <= 0:
        return ValidationIssue(row_number, "quantity", "range_error", "quantity must be greater than 0.", "medium")
    return None


def _valid_timestamp(row: pd.Series, row_number: int):
    if pd.isna(row["order_ts"]):
        return ValidationIssue(row_number, "order_ts", "date_parse_error", "order_ts must be a valid date.", "high")
    return None


def _valid_country(row: pd.Series, row_number: int):
    if row["country"] not in VALID_COUNTRIES:
        return ValidationIssue(row_number, "country", "invalid_domain", "country is outside the accepted domain.", "medium")
    return None


def _valid_payment(row: pd.Series, row_number: int):
    if row["payment_method"] not in VALID_PAYMENT_METHODS:
        return ValidationIssue(
            row_number,
            "payment_method",
            "invalid_domain",
            "payment_method is outside the accepted domain.",
            "medium",
        )
    return None


def _issue_to_dict(issue: ValidationIssue) -> dict:
    return {
        "row_number": issue.row_number,
        "field": issue.field,
        "issue_type": issue.issue_type,
        "message": issue.message,
        "severity": issue.severity,
    }


def _json_safe_record(record: dict) -> dict:
    safe = {}
    for key, value in record.items():
        if pd.isna(value):
            safe[key] = None
        elif hasattr(value, "isoformat"):
            safe[key] = value.isoformat()
        else:
            safe[key] = value
    return safe
