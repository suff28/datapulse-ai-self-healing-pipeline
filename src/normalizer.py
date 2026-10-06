import re
import pandas as pd

from src.contracts import COLUMN_ALIASES, EXPECTED_COLUMNS


def normalize_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    rename_map = {}
    for column in df.columns:
        normalized = _normalize_name(column)
        target = COLUMN_ALIASES.get(normalized, normalized)
        if target in EXPECTED_COLUMNS:
            rename_map[column] = target

    renamed = df.rename(columns=rename_map).copy()
    return renamed, rename_map


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    if "amount" in clean:
        clean["amount"] = pd.to_numeric(clean["amount"], errors="coerce")
    if "quantity" in clean:
        clean["quantity"] = pd.to_numeric(clean["quantity"], errors="coerce").astype("Int64")
    if "order_ts" in clean:
        clean["order_ts"] = pd.to_datetime(clean["order_ts"], errors="coerce", utc=True)
    if "country" in clean:
        clean["country"] = clean["country"].astype(str).str.upper().str.strip()
    if "payment_method" in clean:
        clean["payment_method"] = clean["payment_method"].astype(str).str.lower().str.strip()
    return clean


def _normalize_name(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")
