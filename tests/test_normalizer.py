import pandas as pd

from src.normalizer import coerce_types, normalize_columns


def test_normalize_columns_maps_common_source_aliases():
    df = pd.DataFrame(
        {
            "Order ID": ["ORD-1"],
            "customer": ["CUST-1"],
            "order date": ["2026-01-01"],
            "category": ["books"],
            "price": ["10.5"],
            "qty": ["2"],
            "country": ["us"],
            "payment": ["CARD"],
        }
    )

    normalized, mapping = normalize_columns(df)
    coerced = coerce_types(normalized)

    assert mapping["Order ID"] == "order_id"
    assert "order_id" in coerced.columns
    assert coerced.loc[0, "amount"] == 10.5
    assert coerced.loc[0, "country"] == "US"
    assert coerced.loc[0, "payment_method"] == "card"
