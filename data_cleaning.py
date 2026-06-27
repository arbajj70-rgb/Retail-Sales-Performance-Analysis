#!/usr/bin/env python3
"""
data_cleaning.py
----------------
Demonstrates end-to-end data cleaning on the raw orders dataset:
  1. Load raw CSVs
  2. Inspect and report data quality issues
  3. Fix: nulls, duplicates, date formats, type casting
  4. Validate the cleaned data
  5. Save cleaned output

Run:  python3 data_cleaning.py
"""

import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

BASE = Path(__file__).parent
DATA = BASE / "data"
OUT  = BASE / "outputs"
OUT.mkdir(exist_ok=True)


def load_data():
    log.info("Loading raw data …")
    customers = pd.read_csv(DATA / "customers.csv")
    products  = pd.read_csv(DATA / "products.csv")
    orders    = pd.read_csv(DATA / "orders_raw.csv")
    log.info("  customers: %d rows, %d cols", *customers.shape)
    log.info("  products:  %d rows, %d cols", *products.shape)
    log.info("  orders:    %d rows, %d cols", *orders.shape)
    return customers, products, orders


def audit_quality(customers, products, orders):
    log.info("\n--- DATA QUALITY AUDIT ---")

    # NULLs
    log.info("Null values in customers:\n%s", customers.isnull().sum().to_string())
    log.info("Null values in products:\n%s", products.isnull().sum().to_string())
    log.info("Null values in orders:\n%s", orders.isnull().sum().to_string())

    # Duplicates
    dup_orders = orders.duplicated().sum()
    log.info("Duplicate rows in orders: %d", dup_orders)

    # Date format issues
    bad_dates = orders[pd.to_datetime(orders["order_date"], errors="coerce").isna()]
    log.info("Rows with unparseable dates: %d", len(bad_dates))

    # Negative / zero quantities
    bad_qty = orders[pd.to_numeric(orders["quantity"], errors="coerce").fillna(0) <= 0]
    log.info("Rows with invalid quantity: %d", len(bad_qty))

    return {
        "null_qty":    orders["quantity"].isna().sum(),
        "duplicates":  dup_orders,
        "bad_dates":   len(bad_dates),
        "invalid_qty": len(bad_qty),
    }


def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    log.info("\n--- CLEANING ORDERS ---")
    df = orders.copy()
    original_len = len(df)

    # Step 1: Remove exact duplicate rows
    df.drop_duplicates(inplace=True)
    log.info("Dropped %d duplicate rows", original_len - len(df))

    # Step 2: Fix date formats — handle both YYYY-MM-DD and DD/MM/YYYY
    def parse_date(val):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return pd.to_datetime(val, format=fmt).strftime("%Y-%m-%d")
            except Exception:
                pass
        return None

    df["order_date"] = df["order_date"].astype(str).apply(parse_date)
    bad = df["order_date"].isna().sum()
    if bad:
        log.warning("Dropping %d rows with unparseable dates", bad)
        df.dropna(subset=["order_date"], inplace=True)
    log.info("Dates standardised to YYYY-MM-DD")

    # Step 3: Cast quantity to numeric, drop rows where it is null or <= 0
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    null_qty = df["quantity"].isna().sum()
    if null_qty:
        log.warning("Dropping %d rows with null quantity", null_qty)
        df.dropna(subset=["quantity"], inplace=True)
    df["quantity"] = df["quantity"].astype(int)
    invalid_qty = (df["quantity"] <= 0).sum()
    if invalid_qty:
        log.warning("Dropping %d rows with quantity <= 0", invalid_qty)
        df = df[df["quantity"] > 0]

    # Step 4: Re-check for logical duplicates (same customer+product+date)
    before = len(df)
    df.drop_duplicates(subset=["customer_id", "product_id", "order_date"], inplace=True)
    log.info("Dropped %d logical duplicate order rows", before - len(df))

    # Step 5: Reset order_id to be sequential
    df = df.reset_index(drop=True)
    df["order_id"] = df.index + 1

    log.info("Cleaned orders: %d rows (started with %d)", len(df), original_len)
    return df


def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    df = customers.copy()
    df["name"]   = df["name"].str.strip().str.title()
    df["city"]   = df["city"].str.strip().str.title()
    df["region"] = df["region"].str.strip().str.title()
    df["email"]  = df["email"].str.strip().str.lower()
    return df


def clean_products(products: pd.DataFrame) -> pd.DataFrame:
    df = products.copy()
    df["name"]     = df["name"].str.strip()
    df["category"] = df["category"].str.strip().str.title()
    df["price"]    = pd.to_numeric(df["price"], errors="coerce").round(2)
    bad = df["price"].isna() | (df["price"] <= 0)
    if bad.sum():
        log.warning("Dropping %d products with invalid price", bad.sum())
        df = df[~bad]
    return df


def validate(customers, products, orders):
    log.info("\n--- VALIDATION ---")
    # Referential integrity
    bad_cust = ~orders["customer_id"].isin(customers["customer_id"])
    bad_prod = ~orders["product_id"].isin(products["product_id"])
    log.info("Orders with unknown customer_id: %d", bad_cust.sum())
    log.info("Orders with unknown product_id:  %d", bad_prod.sum())
    log.info("Remaining nulls in orders:\n%s", orders.isnull().sum().to_string())
    log.info("Duplicate rows in cleaned orders: %d", orders.duplicated().sum())
    log.info("Date range: %s  →  %s", orders["order_date"].min(), orders["order_date"].max())
    log.info("Quantity range: %d – %d", orders["quantity"].min(), orders["quantity"].max())


def save_cleaned(customers, products, orders):
    customers.to_csv(DATA / "customers.csv",        index=False)
    products.to_csv(DATA / "products.csv",           index=False)
    orders.to_csv(DATA / "orders.csv",               index=False)
    log.info("\nCleaned files saved to data/")

    # Save a cleaning report
    report = f"""DATA CLEANING REPORT
====================
customers : {len(customers)} rows
products  : {len(products)} rows
orders    : {len(orders)} rows (cleaned)

Issues fixed:
  • Duplicate rows removed
  • Date formats standardised to YYYY-MM-DD
  • Null quantities dropped
  • Invalid quantities (<=0) dropped
  • Logical duplicate orders removed
  • Text fields stripped and title-cased
"""
    (OUT / "cleaning_report.txt").write_text(report)
    log.info("Cleaning report saved → outputs/cleaning_report.txt")


def main():
    customers, products, orders = load_data()
    audit_quality(customers, products, orders)
    orders    = clean_orders(orders)
    customers = clean_customers(customers)
    products  = clean_products(products)
    validate(customers, products, orders)
    save_cleaned(customers, products, orders)
    log.info("\nData cleaning complete.")


if __name__ == "__main__":
    main()
