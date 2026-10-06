import pandas as pd

from src.normalizer import coerce_types
from src.quality import compute_quality_score, flatten_issues, validate_orders


def test_validate_orders_splits_clean_and_quarantined_rows():
    df = pd.DataFrame(
        [
            {
                "order_id": "ORD-1",
                "customer_id": "CUST-1",
                "order_ts": "2026-01-01T00:00:00Z",
                "product_category": "books",
                "amount": 25,
                "quantity": 1,
                "country": "US",
                "payment_method": "card",
            },
            {
                "order_id": "ORD-2",
                "customer_id": "",
                "order_ts": "bad-date",
                "product_category": "electronics",
                "amount": "abc",
                "quantity": -1,
                "country": "XX",
                "payment_method": "crypto",
            },
        ]
    )

    clean, quarantine, global_issues = validate_orders(coerce_types(df))
    issues = flatten_issues(quarantine, global_issues)

    assert len(clean) == 1
    assert len(quarantine) == 1
    assert {issue["issue_type"] for issue in issues} >= {"missing_value", "date_parse_error", "type_error"}


def test_quality_score_penalizes_quarantined_rows():
    assert compute_quality_score(total_rows=100, quarantined_rows=10, schema_failed=False) == 90
    assert compute_quality_score(total_rows=100, quarantined_rows=10, schema_failed=True) == 60
