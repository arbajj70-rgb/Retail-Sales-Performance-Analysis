# Retail-Sales-Performance-Analysis

An end-to-end SQL + Python data analytics project demonstrating:
data cleaning, exploratory analysis, business insights, and visualization.

**Stack:** Python 3 · SQLite · pandas · matplotlib · SQL (window functions, CTEs)

---

## Project Structure

```
retail_analytics/
├── data/
│   ├── customers.csv          # 30 customers with region, city, age, email
│   ├── products.csv           # 25 products across 5 categories
│   ├── orders.csv             # 1,185 cleaned orders (Oct 2025 – Jun 2026)
│   └── orders_raw.csv         # Raw file with intentional data quality issues
│
├── sql/
│   ├── schema.sql             # Tables, constraints, and indexes
│   └── analysis_queries.sql   # 22 queries across 7 analysis sections
│
├── outputs/
│   ├── charts/                # 8 matplotlib charts (PNG)
│   ├── query_results.txt      # All query outputs
│   └── cleaning_report.txt    # Data cleaning log
│
├── generate_dataset.py        # Creates CSVs with realistic data quality issues
├── data_cleaning.py           # Full cleaning pipeline (pandas)
├── run_queries.py             # Builds SQLite DB and runs all SQL queries
├── visualize.py               # Generates all 8 charts
├── results_summary.md         # Business insights with actual numbers
├── requirements.txt           # Python dependencies
└── .gitignore
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate raw dataset
python3 generate_dataset.py

# 3. Clean the data
python3 data_cleaning.py

# 4. Build DB and run queries
python3 run_queries.py

# 5. Generate charts
python3 visualize.py
```

Results appear in `outputs/`. Charts saved to `outputs/charts/`.

---

## Key Findings

| Metric | Value |
|---|---|
| Total Revenue | $156,154 |
| Total Orders | 1,185 |
| Top Category | Electronics ($44,715 / 28.6%) |
| Top Region | West ($54,240 / 34.7%) |
| Top Product | Smartwatch ($16,119) |
| Peak Month | November 2025 (+27.9% MoM) |
| Weekend Revenue Share | 47% of total |

---

## SQL Techniques Demonstrated

- JOINs (INNER, LEFT) across 3 tables
- Aggregate functions (SUM, AVG, COUNT, MAX)
- GROUP BY with all non-aggregated columns correctly listed
- HAVING for filtered aggregation
- CTEs (WITH clause) for readable multi-step queries
- Window functions: RANK(), LAG(), SUM() OVER (running totals)
- CASE WHEN for custom segmentation
- strftime() for date truncation (not SUBSTR)
- DATE('now', '-90 days') for dynamic date filtering
- Subqueries for percentage calculations

---

## Data Cleaning Steps

The raw `orders_raw.csv` had intentional quality issues to demonstrate cleaning skills:

| Issue | Count | Resolution |
|---|---|---|
| Duplicate rows | 10 | `drop_duplicates()` |
| Null quantities | 15 | Drop rows |
| Wrong date format (DD/MM/YYYY) | 8 | Re-parse with `strftime` |

Result: **1,210 → 1,185 clean rows**

---

## Requirements

```
pandas>=2.0
matplotlib>=3.7
seaborn>=0.12
```

---

## About the Data

Synthetic dataset generated with `random.seed(42)` for reproducibility.
Data covers US retail sales across 4 regions (West, South, Midwest, East)
with realistic weekend-heavy order patterns and week-level date distribution.
