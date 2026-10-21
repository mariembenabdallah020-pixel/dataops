import pandas as pd

MAX_UNIT_PRICE = 1000


def _flag(df, mask, reason):
    """Mark the rows selected by `mask` as rejected, unless already rejected."""
    df.loc[mask & df["reject_reason"].isna(), "reject_reason"] = reason


def clean_orders(df):
    """Apply the quality rules. Returns two tables: (clean, rejected)."""
    df = df.copy()
    df["reject_reason"] = None
    # The rules will go here (step 3).
    rejected = df[df["reject_reason"].notna()]
    clean = df[df["reject_reason"].isna()].drop(columns="reject_reason")
    return clean, rejected


def revenue_by_country(clean):
    """Transform: total revenue per country."""
    out = clean.assign(revenue=clean["quantity"] * clean["unit_price"])
    out = out.groupby("country", as_index=False)["revenue"].sum()
    out["revenue"] = out["revenue"].round(2)
    return out