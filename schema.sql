-- =============================================================
-- schema.sql  —  Retail Sales Analytics (SQLite)
-- Includes: tables, constraints, and performance indexes
-- =============================================================

PRAGMA foreign_keys = ON;

-- -------------------------------------------------------------
-- customers
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    city        TEXT,
    region      TEXT,
    email       TEXT    UNIQUE,
    age         INTEGER CHECK(age > 0 AND age < 120)
);

-- -------------------------------------------------------------
-- products
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL,
    category   TEXT,
    price      REAL    NOT NULL CHECK(price > 0)
);

-- -------------------------------------------------------------
-- orders
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id  INTEGER NOT NULL,
    quantity    INTEGER NOT NULL CHECK(quantity > 0),
    order_date  TEXT    NOT NULL,  -- stored as YYYY-MM-DD
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY(product_id)  REFERENCES products(product_id)
);

-- -------------------------------------------------------------
-- Indexes for JOIN and filter performance
-- -------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_orders_customer  ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_product   ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_date      ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_customers_region  ON customers(region);
