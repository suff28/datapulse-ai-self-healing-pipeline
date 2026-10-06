from dataclasses import dataclass


EXPECTED_COLUMNS = [
    "order_id",
    "customer_id",
    "order_ts",
    "product_category",
    "amount",
    "quantity",
    "country",
    "payment_method",
]

COLUMN_ALIASES = {
    "orderid": "order_id",
    "order id": "order_id",
    "customer": "customer_id",
    "customerid": "customer_id",
    "timestamp": "order_ts",
    "order_date": "order_ts",
    "date": "order_ts",
    "category": "product_category",
    "product": "product_category",
    "price": "amount",
    "total_amount": "amount",
    "qty": "quantity",
    "units": "quantity",
    "nation": "country",
    "payment": "payment_method",
}

VALID_PAYMENT_METHODS = {"card", "ach", "paypal", "wire", "apple_pay"}
VALID_COUNTRIES = {"US", "CA", "GB", "IN", "DE", "FR", "AU"}


@dataclass(frozen=True)
class ValidationIssue:
    row_number: int
    field: str
    issue_type: str
    message: str
    severity: str = "medium"
