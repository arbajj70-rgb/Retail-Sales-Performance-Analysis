#!/usr/bin/env python3
"""
visualize.py
------------
Generates all analysis charts from the retail SQLite database.
Requires: retail.db (run run_queries.py first)

Output charts saved to outputs/charts/
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

BASE      = Path(__file__).parent
DB_PATH   = BASE / "retail.db"
CHART_DIR = BASE / "outputs" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

# Style
plt.rcParams.update({
    "figure.dpi":       150,
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.grid":        True,
    "grid.alpha":       0.3,
    "font.family":      "sans-serif",
    "font.size":        11,
})
PALETTE = ["#378ADD", "#1D9E75", "#EF9F27", "#D85A30", "#7F77DD", "#D4537E"]


def get_conn():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "retail.db not found. Run `python3 run_queries.py` first.")
    return sqlite3.connect(str(DB_PATH))


# ------------------------------------------------------------------
# Chart 1: Monthly Revenue Trend
# ------------------------------------------------------------------
def chart_monthly_revenue(conn):
    df = pd.read_sql("""
        SELECT strftime('%Y-%m', o.order_date) AS month,
               ROUND(SUM(o.quantity * p.price), 2) AS revenue
        FROM orders o JOIN products p ON o.product_id = p.product_id
        GROUP BY month ORDER BY month
    """, conn)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["month"], df["revenue"], marker="o", color=PALETTE[0],
            linewidth=2.5, markersize=6)
    ax.fill_between(df["month"], df["revenue"], alpha=0.1, color=PALETTE[0])
    ax.set_title("Monthly Revenue Trend", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    path = CHART_DIR / "01_monthly_revenue.png"
    fig.savefig(path)
    plt.close()
    log.info("Saved: %s", path)


# ------------------------------------------------------------------
# Chart 2: Revenue by Category (horizontal bar)
# ------------------------------------------------------------------
def chart_category_revenue(conn):
    df = pd.read_sql("""
        SELECT p.category,
               ROUND(SUM(o.quantity * p.price), 2) AS revenue
        FROM orders o JOIN products p ON o.product_id = p.product_id
        GROUP BY p.category ORDER BY revenue
    """, conn)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(df["category"], df["revenue"],
                   color=PALETTE[:len(df)], edgecolor="none", height=0.6)
    for bar, val in zip(bars, df["revenue"]):
        ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
                f"${val:,.0f}", va="center", fontsize=10)
    ax.set_title("Revenue by Product Category", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Revenue (USD)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    path = CHART_DIR / "02_category_revenue.png"
    fig.savefig(path)
    plt.close()
    log.info("Saved: %s", path)


# ------------------------------------------------------------------
# Chart 3: Revenue by Region (pie)
# ------------------------------------------------------------------
def chart_region_pie(conn):
    df = pd.read_sql("""
        SELECT c.region,
               ROUND(SUM(o.quantity * p.price), 2) AS revenue
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.region ORDER BY revenue DESC
    """, conn)

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        df["revenue"], labels=df["region"],
        autopct="%1.1f%%", colors=PALETTE[:len(df)],
        startangle=140, pctdistance=0.82,
        wedgeprops={"edgecolor": "white", "linewidth": 2}
    )
    for t in autotexts:
        t.set_fontsize(10)
    ax.set_title("Revenue by Region", fontsize=14, fontweight="bold", pad=12)
    plt.tight_layout()
    path = CHART_DIR / "03_region_pie.png"
    fig.savefig(path)
    plt.close()
    log.info("Saved: %s", path)


# ------------------------------------------------------------------
# Chart 4: Top 10 Products by Revenue
# ------------------------------------------------------------------
def chart_top_products(conn):
    df = pd.read_sql("""
        SELECT p.name AS product,
               ROUND(SUM(o.quantity * p.price), 2) AS revenue
        FROM orders o JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_id, p.name
        ORDER BY revenue DESC LIMIT 10
    """, conn)
    df = df.sort_values("revenue")

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(df["product"], df["revenue"],
                   color=PALETTE[0], edgecolor="none", height=0.6)
    for bar, val in zip(bars, df["revenue"]):
        ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height() / 2,
                f"${val:,.0f}", va="center", fontsize=9)
    ax.set_title("Top 10 Products by Revenue", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Revenue (USD)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    path = CHART_DIR / "04_top_products.png"
    fig.savefig(path)
    plt.close()
    log.info("Saved: %s", path)


# ------------------------------------------------------------------
# Chart 5: Top 10 Customers by Spend
# ------------------------------------------------------------------
def chart_top_customers(conn):
    df = pd.read_sql("""
        SELECT c.name AS customer,
               ROUND(SUM(o.quantity * p.price), 2) AS spend
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY spend DESC LIMIT 10
    """, conn)
    df = df.sort_values("spend")

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(df["customer"], df["spend"],
            color=PALETTE[1], edgecolor="none", height=0.6)
    ax.set_title("Top 10 Customers by Total Spend", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Total Spend (USD)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    path = CHART_DIR / "05_top_customers.png"
    fig.savefig(path)
    plt.close()
    log.info("Saved: %s", path)


# ------------------------------------------------------------------
# Chart 6: Quantity distribution (histogram)
# ------------------------------------------------------------------
def chart_quantity_dist(conn):
    df = pd.read_sql("SELECT quantity FROM orders", conn)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(df["quantity"], bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
            color=PALETTE[2], edgecolor="white", rwidth=0.8)
    ax.set_title("Order Quantity Distribution", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Quantity per Order Line")
    ax.set_ylabel("Number of Orders")
    ax.set_xticks([1, 2, 3, 4, 5])
    plt.tight_layout()
    path = CHART_DIR / "06_quantity_dist.png"
    fig.savefig(path)
    plt.close()
    log.info("Saved: %s", path)


# ------------------------------------------------------------------
# Chart 7: Day-of-week revenue heatmap
# ------------------------------------------------------------------
def chart_dow_revenue(conn):
    df = pd.read_sql("""
        SELECT
            CASE strftime('%w', order_date)
                WHEN '0' THEN 'Sun' WHEN '1' THEN 'Mon' WHEN '2' THEN 'Tue'
                WHEN '3' THEN 'Wed' WHEN '4' THEN 'Thu' WHEN '5' THEN 'Fri'
                WHEN '6' THEN 'Sat'
            END AS dow,
            strftime('%w', order_date) AS dow_num,
            ROUND(SUM(o.quantity * p.price), 2) AS revenue
        FROM orders o JOIN products p ON o.product_id = p.product_id
        GROUP BY dow, dow_num ORDER BY dow_num
    """, conn)

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = [PALETTE[0] if d in ("Sat", "Sun") else PALETTE[5]
              for d in df["dow"]]
    ax.bar(df["dow"], df["revenue"], color=colors, edgecolor="none", width=0.6)
    ax.set_title("Revenue by Day of Week", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("Revenue (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=PALETTE[0], label="Weekend"),
                        Patch(color=PALETTE[5], label="Weekday")], fontsize=9)
    plt.tight_layout()
    path = CHART_DIR / "07_dow_revenue.png"
    fig.savefig(path)
    plt.close()
    log.info("Saved: %s", path)


# ------------------------------------------------------------------
# Chart 8: Customer age group spend
# ------------------------------------------------------------------
def chart_age_group(conn):
    df = pd.read_sql("""
        SELECT
            CASE
                WHEN c.age BETWEEN 18 AND 29 THEN '18-29'
                WHEN c.age BETWEEN 30 AND 39 THEN '30-39'
                WHEN c.age BETWEEN 40 AND 49 THEN '40-49'
                ELSE '50+'
            END AS age_group,
            ROUND(SUM(o.quantity * p.price), 2) AS revenue
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN products p ON o.product_id = p.product_id
        GROUP BY age_group ORDER BY age_group
    """, conn)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(df["age_group"], df["revenue"],
           color=PALETTE[3], edgecolor="none", width=0.5)
    ax.set_title("Revenue by Customer Age Group", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Age Group")
    ax.set_ylabel("Revenue (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    path = CHART_DIR / "08_age_group_revenue.png"
    fig.savefig(path)
    plt.close()
    log.info("Saved: %s", path)


def main():
    conn = get_conn()
    try:
        log.info("Generating charts …")
        chart_monthly_revenue(conn)
        chart_category_revenue(conn)
        chart_region_pie(conn)
        chart_top_products(conn)
        chart_top_customers(conn)
        chart_quantity_dist(conn)
        chart_dow_revenue(conn)
        chart_age_group(conn)
        log.info("\nAll 8 charts saved to outputs/charts/")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
