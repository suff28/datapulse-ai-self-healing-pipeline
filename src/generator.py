import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Union
import pandas as pd


PRODUCTS = ["electronics", "books", "grocery", "fitness", "home", "beauty", "software"]
COUNTRIES = ["US", "CA", "GB", "IN", "DE", "FR", "AU"]
PAYMENTS = ["card", "ach", "paypal", "wire", "apple_pay"]


def generate_orders(path: Union[str, Path], rows: int = 250, messy: bool = True) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    records = []
    base_time = datetime.now(timezone.utc) - timedelta(days=3)

    for idx in range(rows):
        records.append(
            {
                "order_id": f"ORD-{100000 + idx}",
                "customer_id": f"CUST-{random.randint(1000, 1080)}",
                "order_ts": (base_time + timedelta(minutes=random.randint(0, 5000))).isoformat(),
                "product_category": random.choice(PRODUCTS),
                "amount": round(random.lognormvariate(4.2, 0.7), 2),
                "quantity": random.randint(1, 5),
                "country": random.choice(COUNTRIES),
                "payment_method": random.choice(PAYMENTS),
            }
        )

    df = pd.DataFrame(records)
    if messy:
        df = inject_messy_records(df)
    df.to_csv(output, index=False)
    return output


def inject_messy_records(df: pd.DataFrame) -> pd.DataFrame:
    messy = df.copy()
    messy["amount"] = messy["amount"].astype("object")
    messy["quantity"] = messy["quantity"].astype("object")
    if len(messy) < 20:
        return messy

    messy.loc[2, "amount"] = "not_available"
    messy.loc[5, "quantity"] = -2
    messy.loc[9, "order_ts"] = "13/44/2026"
    messy.loc[12, "payment_method"] = "bitcoin"
    messy.loc[15, "country"] = "XX"
    messy.loc[18, "customer_id"] = ""
    messy.loc[22, "order_id"] = messy.loc[21, "order_id"]
    messy.loc[25, "amount"] = -99
    messy.loc[27, "quantity"] = "many"

    alias_df = messy.rename(
        columns={
            "order_id": "Order ID",
            "customer_id": "customer",
            "order_ts": "order date",
            "product_category": "category",
            "amount": "price",
            "quantity": "qty",
            "payment_method": "payment",
        }
    )
    return alias_df.sample(frac=1, random_state=42).reset_index(drop=True)
