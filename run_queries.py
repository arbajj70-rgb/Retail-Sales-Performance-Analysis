#!/usr/bin/env python3
"""
run_queries.py
--------------
Builds the SQLite retail database from schema + seed files,
runs all analysis queries, prints results to console,
and exports each result set to outputs/query_results.txt.

Usage:
    python3 run_queries.py
    python3 run_queries.py --db my_custom.db
    python3 run_queries.py --section revenue
"""

import argparse
import logging
import sqlite3
import csv
from pathlib import Path

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
BASE    = Path(__file__).parent
SQL_DIR = BASE / "sql"
DATA    = BASE / "data"
OUT     = BASE / "outputs"
OUT.mkdir(exist_ok=True)

SCHEMA  = SQL_DIR / "schema.sql"
QUERIES = SQL_DIR / "analysis_queries.sql"

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def load_sql(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8")


def build_database(conn: sqlite3.Connection) -> None:
    """Create schema and seed data from CSV files."""
    log.info("Creating schema …")
    conn.executescript(load_sql(SCHEMA))

    # Seed from CSV files
    log.info("Loading customers …")
    _load_csv(conn, DATA / "customers.csv", "customers",
              ["customer_id", "name", "city", "region", "email", "age"])

    log.info("Loading products …")
    _load_csv(conn, DATA / "products.csv", "products",
              ["product_id", "name", "category", "price"])

    log.info("Loading orders …")
    _load_csv(conn, DATA / "orders.csv", "orders",
              ["order_id", "customer_id", "product_id", "quantity", "order_date"])

    conn.commit()
    log.info("Database ready.")


def _load_csv(conn, path: Path, table: str, columns: list) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    placeholders = ", ".join("?" * len(columns))
    col_list = ", ".join(columns)
    sql = f"INSERT OR IGNORE INTO {table} ({col_list}) VALUES ({placeholders})"
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            vals = []
            for col in columns:
                v = row.get(col, "").strip()
                vals.append(None if v == "" else v)
            rows.append(vals)
    conn.executemany(sql, rows)
    log.info("  → inserted %d rows into %s", len(rows), table)


def extract_named_queries(sql_text: str) -> list[tuple[str, str]]:
    """
    Parse named query blocks from SQL file.
    Each block starts with a comment like:  -- 2a. Total revenue
    Returns list of (label, sql) tuples.
    """
    import re
    pattern = re.compile(r"--\s+(\d+[a-z]\.\s+.+?)$(.*?)(?=\n--\s+\d+[a-z]\.|\Z)",
                         re.DOTALL | re.MULTILINE)
    results = []
    for m in pattern.finditer(sql_text):
        label = m.group(1).strip()
        body  = m.group(2).strip()
        # Only keep SELECT / WITH blocks
        selects = [s.strip() for s in re.split(r"\n\n+", body)
                   if s.strip().upper().startswith(("SELECT", "WITH"))]
        if selects:
            results.append((label, selects[0]))
    return results


def run_queries(conn: sqlite3.Connection, section_filter: str | None) -> None:
    sql_text = load_sql(QUERIES)
    named = extract_named_queries(sql_text)

    if not named:
        log.warning("No named queries found. Check analysis_queries.sql format.")
        return

    output_lines = []

    for label, query in named:
        if section_filter and section_filter.lower() not in label.lower():
            continue
        log.info("Running: %s", label)
        try:
            cur = conn.execute(query)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
        except sqlite3.Error as e:
            log.error("Query failed [%s]: %s", label, e)
            continue

        # Console output
        header = f"\n{'='*60}\n  {label}\n{'='*60}"
        print(header)
        if cols:
            col_widths = [max(len(c), max((len(str(r[i])) for r in rows), default=0))
                          for i, c in enumerate(cols)]
            fmt = "  " + "  ".join(f"{{:<{w}}}" for w in col_widths)
            print(fmt.format(*cols))
            print("  " + "  ".join("-" * w for w in col_widths))
            for r in rows:
                print(fmt.format(*[str(v) if v is not None else "NULL" for v in r]))
        print(f"  ({len(rows)} row{'s' if len(rows) != 1 else ''})")

        output_lines.append(header)
        if cols:
            output_lines.append("  " + " | ".join(cols))
        for r in rows:
            output_lines.append("  " + " | ".join(str(v) if v is not None else "NULL" for v in r))
        output_lines.append(f"  ({len(rows)} rows)")

    # Save to file
    result_file = OUT / "query_results.txt"
    result_file.write_text("\n".join(output_lines), encoding="utf-8")
    log.info("Results saved → %s", result_file)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Run retail analytics queries")
    parser.add_argument("--db",      default="retail.db",
                        help="SQLite DB filename (default: retail.db)")
    parser.add_argument("--section", default=None,
                        help="Filter queries by keyword, e.g. 'revenue' or 'customer'")
    parser.add_argument("--rebuild", action="store_true",
                        help="Force rebuild the database even if it exists")
    args = parser.parse_args()

    db_path = BASE / args.db
    if args.rebuild and db_path.exists():
        db_path.unlink()
        log.info("Removed existing database.")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    try:
        # Only build if db is empty
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        if not tables or args.rebuild:
            build_database(conn)
        else:
            log.info("Using existing database: %s", db_path)

        run_queries(conn, args.section)
    except FileNotFoundError as e:
        log.error("%s", e)
    finally:
        conn.commit()
        conn.close()


if __name__ == "__main__":
    main()
