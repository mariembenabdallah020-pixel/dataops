REQUIRED_COLUMNS = [
"order_id",
"order_date",
"customer_id",
"country",

"product",
"quantity",
"unit_price",
]
MAX_REJECT_RATE = 0.20


class DataQualityError(Exception):
    """Raised when the data is not good enough to continue."""


def check_schema(df):
    """Stop if a required column is missing or if the file is empty."""
    pass


def check_reject_rate(n_total, n_rejected, max_rate=MAX_REJECT_RATE):
    """Stop if too large a share of the rows was rejected."""
    pass
