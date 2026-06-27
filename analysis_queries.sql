-- =============================================================
-- analysis_queries.sql  —  Retail Sales Analytics
-- All queries tested on SQLite 3.x
-- Fixes applied:
--   • All non-aggregated SELECT columns present in GROUP BY
--   • ROUND() on every revenue output
--   • strftime() instead of SUBSTR() for date truncation
--   • DATE('now','-90 days') instead of hardcoded date
--   • Indexes referenced in schema.sql for performance
--   • Window functions added (RANK, running total)
-- =============================================================


-- =============================================================
-- SECTION 1: DATA QUALITY CHECKS
-- =============================================================

-- 1a. NULL check across all critical columns
SELECT
    (SELECT COUNT(*) FROM customers WHERE name     IS NULL) AS customers_name_nulls,
    (SELECT COUNT(*) FROM customers WHERE region   IS NULL) AS customers_region_nulls,
    (SELECT COUNT(*) FROM products  WHERE price    IS NULL) AS products_price_nulls,
    (SELECT COUNT(*) FROM orders    WHERE order_date IS NULL) AS orders_date_nulls,
    (SELECT COUNT(*) FROM orders    WHERE quantity  IS NULL) AS orders_qty_nulls;

-- 1b. Duplicate orders (same customer + product + date)
SELECT
    customer_id,
    product_id,
    order_date,
    COUNT(*) AS duplicate_count
FROM orders
GROUP BY customer_id, product_id, order_date
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- 1c. Orphan check: orders referencing non-existent customers
SELECT o.order_id, o.customer_id
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- 1d. Orphan check: orders referencing non-existent products
SELECT o.order_id, o.product_id
FROM orders o
LEFT JOIN products p ON o.product_id = p.product_id
WHERE p.product_id IS NULL;

-- 1e. Invalid date format check (should return 0 rows)
SELECT order_id, order_date
FROM orders
WHERE date(order_date) IS NULL;

-- 1f. Out-of-range quantity check
SELECT order_id, quantity
FROM orders
WHERE quantity <= 0 OR quantity > 100;


-- =============================================================
-- SECTION 2: REVENUE SUMMARY
-- =============================================================

-- 2a. Total revenue
SELECT ROUND(SUM(o.quantity * p.price), 2) AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id;

-- 2b. Total orders, total units sold, average order value
SELECT
    COUNT(DISTINCT o.order_id)                          AS total_orders,
    SUM(o.quantity)                                     AS total_units_sold,
    ROUND(AVG(o.quantity * p.price), 2)                 AS avg_line_value,
    ROUND(SUM(o.quantity * p.price), 2)                 AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id;


-- =============================================================
-- SECTION 3: CATEGORY & PRODUCT ANALYSIS
-- =============================================================

-- 3a. Revenue by category (fixed: category in both SELECT and GROUP BY)
SELECT
    p.category,
    ROUND(SUM(o.quantity * p.price), 2)                     AS revenue,
    SUM(o.quantity)                                          AS units_sold,
    COUNT(DISTINCT o.order_id)                               AS num_orders
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- 3b. Top 10 best-selling products by revenue (fixed GROUP BY)
SELECT
    p.product_id,
    p.name        AS product_name,
    p.category,
    SUM(o.quantity)                              AS total_units,
    ROUND(SUM(o.quantity * p.price), 2)          AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY total_revenue DESC
LIMIT 10;

-- 3c. Product revenue rank within each category (window function)
SELECT
    p.category,
    p.name                                                AS product_name,
    ROUND(SUM(o.quantity * p.price), 2)                   AS revenue,
    RANK() OVER (
        PARTITION BY p.category
        ORDER BY SUM(o.quantity * p.price) DESC
    ) AS rank_in_category
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY p.category, rank_in_category;


-- =============================================================
-- SECTION 4: REGIONAL ANALYSIS
-- =============================================================

-- 4a. Revenue by region (fixed GROUP BY)
SELECT
    c.region,
    ROUND(SUM(o.quantity * p.price), 2)          AS revenue,
    COUNT(DISTINCT o.customer_id)                AS unique_customers,
    COUNT(DISTINCT o.order_id)                   AS num_orders
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY revenue DESC;

-- 4b. Best product-region combination
SELECT
    p.name         AS product_name,
    c.region,
    ROUND(SUM(o.quantity * p.price), 2) AS revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY p.product_id, p.name, c.region
ORDER BY revenue DESC
LIMIT 5;


-- =============================================================
-- SECTION 5: TIME-SERIES ANALYSIS
-- =============================================================

-- 5a. Monthly revenue trend (strftime instead of SUBSTR)
SELECT
    strftime('%Y-%m', order_date)                AS month,
    ROUND(SUM(o.quantity * p.price), 2)          AS revenue,
    COUNT(DISTINCT o.order_id)                   AS num_orders,
    SUM(o.quantity)                              AS units_sold
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;

-- 5b. Running cumulative revenue by month (window function)
SELECT
    month,
    revenue,
    ROUND(SUM(revenue) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING), 2) AS cumulative_revenue
FROM (
    SELECT
        strftime('%Y-%m', order_date)               AS month,
        ROUND(SUM(o.quantity * p.price), 2)         AS revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY strftime('%Y-%m', order_date)
) t
ORDER BY month;

-- 5c. Day-of-week revenue pattern
SELECT
    CASE strftime('%w', order_date)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END                                          AS day_of_week,
    ROUND(SUM(o.quantity * p.price), 2)          AS revenue,
    COUNT(DISTINCT o.order_id)                   AS num_orders
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY strftime('%w', order_date)
ORDER BY strftime('%w', order_date);


-- =============================================================
-- SECTION 6: CUSTOMER ANALYSIS
-- =============================================================

-- 6a. Average order value per customer (fixed GROUP BY)
SELECT
    c.customer_id,
    c.name                                           AS customer_name,
    c.region,
    COUNT(DISTINCT o.order_id)                       AS total_orders,
    ROUND(SUM(o.quantity * p.price), 2)              AS total_spend,
    ROUND(AVG(o.quantity * p.price), 2)              AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name, c.region
ORDER BY total_spend DESC;

-- 6b. Top 10 customers by revenue with contribution % (fixed GROUP BY)
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.name,
        c.region,
        ROUND(SUM(o.quantity * p.price), 2) AS revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY c.customer_id, c.name, c.region
),
total AS (
    SELECT SUM(revenue) AS grand_total FROM customer_revenue
)
SELECT
    cr.customer_id,
    cr.name,
    cr.region,
    cr.revenue,
    ROUND(100.0 * cr.revenue / t.grand_total, 2) AS pct_of_total,
    RANK() OVER (ORDER BY cr.revenue DESC)        AS revenue_rank
FROM customer_revenue cr, total t
ORDER BY cr.revenue DESC
LIMIT 10;

-- 6c. Churned customers: no order in last 90 days (dynamic date)
SELECT
    c.customer_id,
    c.name,
    c.region,
    MAX(o.order_date)                           AS last_order_date,
    CASE
        WHEN MAX(o.order_date) IS NULL THEN 'Never ordered'
        ELSE 'Inactive 90+ days'
    END                                         AS churn_reason
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.region
HAVING MAX(o.order_date) IS NULL
    OR DATE(MAX(o.order_date)) <= DATE('now', '-90 days')
ORDER BY last_order_date;

-- 6d. Repeat vs one-time buyers
SELECT
    purchase_segment,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM (
    SELECT
        c.customer_id,
        CASE
            WHEN COUNT(DISTINCT o.order_id) = 1 THEN 'One-time buyer'
            WHEN COUNT(DISTINCT o.order_id) BETWEEN 2 AND 4 THEN 'Occasional (2-4 orders)'
            ELSE 'Loyal (5+ orders)'
        END AS purchase_segment
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
) t
GROUP BY purchase_segment
ORDER BY customer_count DESC;

-- 6e. Customer age group analysis
SELECT
    CASE
        WHEN c.age BETWEEN 18 AND 29 THEN '18-29'
        WHEN c.age BETWEEN 30 AND 39 THEN '30-39'
        WHEN c.age BETWEEN 40 AND 49 THEN '40-49'
        ELSE '50+'
    END                                         AS age_group,
    COUNT(DISTINCT c.customer_id)               AS customers,
    ROUND(SUM(o.quantity * p.price), 2)         AS revenue,
    ROUND(AVG(o.quantity * p.price), 2)         AS avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY age_group
ORDER BY age_group;


-- =============================================================
-- SECTION 7: ADVANCED ANALYTICS
-- =============================================================

-- 7a. Month-over-month revenue growth %
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month)                        AS prev_month_revenue,
    CASE
        WHEN LAG(revenue) OVER (ORDER BY month) IS NULL THEN NULL
        ELSE ROUND(
            100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
                  / LAG(revenue) OVER (ORDER BY month), 1)
    END                                                       AS mom_growth_pct
FROM (
    SELECT
        strftime('%Y-%m', order_date)               AS month,
        ROUND(SUM(o.quantity * p.price), 2)         AS revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY strftime('%Y-%m', order_date)
) t
ORDER BY month;

-- 7b. Revenue contribution by region with % (window function)
SELECT
    c.region,
    ROUND(SUM(o.quantity * p.price), 2)                       AS revenue,
    ROUND(
        100.0 * SUM(o.quantity * p.price)
              / SUM(SUM(o.quantity * p.price)) OVER (), 1
    )                                                         AS pct_of_total
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY revenue DESC;
