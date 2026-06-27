# Results Summary & Business Insights

## Project Overview
Retail sales analysis on **30 customers**, **25 products**, and **1,185 cleaned orders** spanning
October 2025 – June 2026 across 4 US regions (West, South, Midwest, East).

---

## Key Metrics

| Metric | Value |
|---|---|
| Total Revenue | **$156,154.02** |
| Total Orders | **1,185** |
| Total Units Sold | **2,516** |
| Average Order Value | **$131.78** |
| Date Range | Oct 2025 – Jun 2026 |

---

## 1. Category Performance

| Category | Revenue | Units Sold | Orders |
|---|---|---|---|
| Electronics | $44,715.29 | 611 | 292 |
| Home | $42,186.98 | 567 | 268 |
| Sports | $32,595.13 | 487 | 233 |
| Clothing | $27,278.26 | 656 | 304 |
| Accessories | $9,378.36 | 195 | 88 |

**Insight:** Electronics leads in revenue despite not having the highest order count,
driven by high-ticket items like the Smartwatch ($199). Clothing leads in units sold
but has lower average price.

---

## 2. Regional Sales

| Region | Revenue | Share |
|---|---|---|
| West | $54,240.06 | 34.7% |
| South | $48,928.43 | 31.3% |
| Midwest | $27,762.21 | 17.8% |
| East | $25,223.32 | 16.2% |

**Insight:** West and South together account for 66% of total revenue.
Midwest and East are underperforming and may benefit from targeted campaigns.

---

## 3. Top 5 Products by Revenue

| Rank | Product | Category | Revenue |
|---|---|---|---|
| 1 | Smartwatch | Electronics | $16,119.00 |
| 2 | Cookware Set | Home | $12,720.00 |
| 3 | Running Shoes | Sports | $12,328.63 |
| 4 | Vacuum Cleaner | Home | $11,352.00 |
| 5 | Hiking Boots | Sports | $10,679.11 |

**Insight:** The top 5 products contribute **$63,199** (40.5%) of total revenue.
Three of the top 5 are high-price items (Smartwatch, Cookware Set, Vacuum Cleaner).

---

## 4. Monthly Revenue Trend

| Month | Revenue | MoM Growth |
|---|---|---|
| Oct 2025 | $17,127.56 | — |
| Nov 2025 | $21,900.77 | +27.9% |
| Dec 2025 | $16,770.16 | -23.4% |
| Jan 2026 | $19,356.95 | +15.4% |
| Feb 2026 | $17,762.70 | -8.2% |
| Mar 2026 | $18,089.48 | +1.8% |
| Apr 2026 | $16,571.92 | -8.4% |
| May 2026 | $20,913.09 | +26.2% |
| Jun 2026 | $7,661.39 | (partial month) |

**Insight:** November and May are peak months. The December dip is unusual for retail
and may reflect the synthetic nature of the data. In real data, December would typically
be the highest month due to holiday spending.

---

## 5. Day of Week Pattern

| Day | Revenue | Orders |
|---|---|---|
| Sunday | $37,509.03 | 278 |
| Saturday | $36,050.72 | 272 |
| Monday | $18,038.99 | 137 |
| Wednesday | $17,445.86 | 128 |

**Insight:** Weekends generate ~47% of total revenue despite being only 2/7 days.
This has strong implications for marketing spend timing — weekend ad budgets should be higher.

---

## 6. Customer Insights

**Top customer:** Omar Hassan (Midwest) — $7,720.41 total spend

**Top 10 customers contribute 41.1% of total revenue**, indicating moderate customer concentration.

**Age group breakdown:**
- 30–39 age group generates the highest revenue ($65,340 / 41.8%)
- 18–29 group shows high average order value ($133.29) relative to their count

**Churn:** 0 customers inactive for 90+ days as of the analysis date (Jun 2026)
— all customers ordered within the window.

---

## 7. Data Cleaning Summary

The raw `orders_raw.csv` contained the following issues (all fixed):

| Issue | Count | Fix Applied |
|---|---|---|
| Duplicate rows | 10 | Removed exact duplicates |
| Null quantities | 15 | Rows dropped |
| Invalid date format (DD/MM/YYYY) | 8 | Re-parsed and standardised |
| Logical duplicate orders | 0 | Verified clean |

**Result:** 1,210 raw rows → 1,185 clean rows

---

## 8. Resume-Ready Bullet Points

- Designed a 3-table normalized SQLite schema (customers, products, orders) with FK constraints and 5 performance indexes
- Wrote 22 SQL queries covering revenue analysis, cohort segmentation, window functions (RANK, LAG, running totals), and churn detection
- Cleaned 1,210-row raw dataset: resolved 10 duplicates, 15 null quantities, and 8 inconsistent date formats using Python (pandas)
- Identified West region (34.7%) and Electronics category ($44,715) as top revenue drivers
- Generated 8 matplotlib visualizations including monthly trend, day-of-week pattern, and product/region breakdown

---

## Next Steps
- Add Power BI / Tableau Public dashboard for interactive exploration
- Implement customer RFM (Recency, Frequency, Monetary) segmentation
- Add a returns/refunds table and profitability analysis
- Expand to 3+ years of data for proper seasonality analysis
