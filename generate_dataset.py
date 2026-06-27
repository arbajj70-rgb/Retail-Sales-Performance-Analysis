#!/usr/bin/env python3
"""
generate_dataset.py
-------------------
Generates realistic retail sales CSVs with intentional data quality issues
(nulls, duplicates, format inconsistencies) to demonstrate data cleaning skills.

Outputs: data/customers.csv, data/products.csv, data/orders.csv
"""

from pathlib import Path
from datetime import date, timedelta
import random

BASE = Path(__file__).parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

random.seed(42)

# ------------------------------------------------------------------
# Master data
# ------------------------------------------------------------------
customers = [
    (1,  "Alice Johnson",   "Seattle",       "West",    "alice.johnson@email.com",   28),
    (2,  "Bob Smith",       "Portland",      "West",    "bob.smith@email.com",        35),
    (3,  "Carlos Diaz",     "Austin",        "South",   "carlos.diaz@email.com",      42),
    (4,  "Diana Lee",       "Boston",        "East",    "diana.lee@email.com",        31),
    (5,  "Eve Martin",      "Miami",         "South",   "eve.martin@email.com",       26),
    (6,  "Frank Zhou",      "Chicago",       "Midwest", "frank.zhou@email.com",       38),
    (7,  "Grace Park",      "San Francisco", "West",    "grace.park@email.com",       29),
    (8,  "Hiro Tanaka",     "New York",      "East",    "hiro.tanaka@email.com",      45),
    (9,  "Ingrid Berg",     "Minneapolis",   "Midwest", "ingrid.berg@email.com",      33),
    (10, "Jack Liu",        "Denver",        "West",    "jack.liu@email.com",         40),
    (11, "Karen Patel",     "Atlanta",       "South",   "karen.patel@email.com",      27),
    (12, "Leo Nguyen",      "Dallas",        "South",   "leo.nguyen@email.com",       36),
    (13, "Maya Green",      "Philadelphia",  "East",    "maya.green@email.com",       32),
    (14, "Nina Rossi",      "Phoenix",       "West",    "nina.rossi@email.com",       44),
    (15, "Omar Hassan",     "Columbus",      "Midwest", "omar.hassan@email.com",      39),
    (16, "Priya Singh",     "San Jose",      "West",    "priya.singh@email.com",      30),
    (17, "Quincy Park",     "Houston",       "South",   "quincy.park@email.com",      47),
    (18, "Rosa Jimenez",    "Las Vegas",     "West",    "rosa.jimenez@email.com",     25),
    (19, "Samir Khan",      "Minneapolis",   "Midwest", "samir.khan@email.com",       41),
    (20, "Tina Adams",      "Orlando",       "South",   "tina.adams@email.com",       34),
    (21, "Uma Patel",       "Seattle",       "West",    "uma.patel@email.com",        29),
    (22, "Victor Cruz",     "Miami",         "South",   "victor.cruz@email.com",      37),
    (23, "Wendy Cho",       "Chicago",       "Midwest", "wendy.cho@email.com",        43),
    (24, "Xander Reed",     "Boston",        "East",    "xander.reed@email.com",      28),
    (25, "Yuki Tanaka",     "San Francisco", "West",    "yuki.tanaka@email.com",      31),
    (26, "Zoe Williams",    "Dallas",        "South",   "zoe.williams@email.com",     26),
    (27, "Aaron Brooks",    "Denver",        "West",    "aaron.brooks@email.com",     48),
    (28, "Bella Torres",    "Atlanta",       "South",   "bella.torres@email.com",     33),
    (29, "Caleb Morris",    "Phoenix",       "West",    "caleb.morris@email.com",     36),
    (30, "Daisy Wang",      "New York",      "East",    "daisy.wang@email.com",       40),
]

products = [
    (1,  "Wireless Headphones", "Electronics",  99.99),
    (2,  "Bluetooth Speaker",   "Electronics",  49.50),
    (3,  "T-Shirt",             "Clothing",     19.99),
    (4,  "Jeans",               "Clothing",     49.99),
    (5,  "Coffee Maker",        "Home",         79.00),
    (6,  "Vacuum Cleaner",      "Home",        129.00),
    (7,  "Smartwatch",          "Electronics", 199.00),
    (8,  "Jacket",              "Clothing",     89.50),
    (9,  "Blender",             "Home",         39.99),
    (10, "Socks 3 Pack",        "Clothing",      9.99),  # removed parentheses
    (11, "Gaming Mouse",        "Electronics",  59.99),
    (12, "Yoga Mat",            "Sports",       24.99),
    (13, "Water Bottle",        "Sports",       14.99),
    (14, "Desk Lamp",           "Home",         29.99),
    (15, "Sneakers",            "Clothing",     74.99),
    (16, "Wireless Charger",    "Electronics",  29.99),
    (17, "Backpack",            "Accessories",  39.99),
    (18, "Sunglasses",          "Accessories",  59.50),
    (19, "Cookware Set",        "Home",        159.00),
    (20, "Hiking Boots",        "Sports",      119.99),
    (21, "Running Shoes",       "Sports",       89.99),
    (22, "Laptop Stand",        "Electronics",  44.99),
    (23, "Throw Blanket",       "Home",         34.99),
    (24, "Cap",                 "Clothing",     19.99),
    (25, "Dumbbells Set",       "Sports",       69.99),
]

start_date = date(2025, 10, 1)
end_date   = date(2026, 6, 15)

all_dates = []
d = start_date
while d <= end_date:
    # Weekends get ~1.6x more orders (retail pattern)
    count = 2 if d.weekday() >= 5 else 1
    all_dates.extend([d.isoformat()] * count)
    d += timedelta(days=1)

# ------------------------------------------------------------------
# Generate 1200 clean orders (no duplication on same customer+product+date)
# ------------------------------------------------------------------
clean_orders = []
seen = set()
order_id = 1
attempts = 0
while len(clean_orders) < 1200 and attempts < 50000:
    attempts += 1
    cid = random.randint(1, len(customers))
    pid = random.randint(1, len(products))
    odate = random.choice(all_dates)
    qty = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
    key = (cid, pid, odate)
    if key in seen:
        continue
    seen.add(key)
    clean_orders.append((order_id, cid, pid, qty, odate))
    order_id += 1

# ------------------------------------------------------------------
# Intentionally inject data quality issues for demonstration
# (will be caught and cleaned by the data cleaning script)
# ------------------------------------------------------------------
dirty_orders = [list(r) for r in clean_orders]

# Issue 1: 15 rows with NULL quantity (represented as empty string in CSV)
null_qty_indices = random.sample(range(len(dirty_orders)), 15)
for i in null_qty_indices:
    dirty_orders[i][3] = ""

# Issue 2: 10 duplicate rows
dup_indices = random.sample(range(100, 400), 10)
for i in dup_indices:
    dirty_orders.append(dirty_orders[i][:])  # exact copy

# Issue 3: 8 rows with inconsistent date format (DD/MM/YYYY instead of YYYY-MM-DD)
bad_date_indices = random.sample(range(400, 800), 8)
for i in bad_date_indices:
    iso = dirty_orders[i][4]
    y, m, day = iso.split("-")
    dirty_orders[i][4] = f"{day}/{m}/{y}"

# ------------------------------------------------------------------
# Write customers CSV (clean)
# ------------------------------------------------------------------
with (DATA / "customers.csv").open("w", encoding="utf-8") as f:
    f.write("customer_id,name,city,region,email,age\n")
    for r in customers:
        f.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]}\n")

# ------------------------------------------------------------------
# Write products CSV (clean)
# ------------------------------------------------------------------
with (DATA / "products.csv").open("w", encoding="utf-8") as f:
    f.write("product_id,name,category,price\n")
    for r in products:
        f.write(f"{r[0]},{r[1]},{r[2]},{r[3]:.2f}\n")

# ------------------------------------------------------------------
# Write orders CSV (with intentional issues for cleaning demo)
# ------------------------------------------------------------------
with (DATA / "orders_raw.csv").open("w", encoding="utf-8") as f:
    f.write("order_id,customer_id,product_id,quantity,order_date\n")
    for r in dirty_orders:
        f.write(",".join(str(x) for x in r) + "\n")

# Also write the clean version
with (DATA / "orders.csv").open("w", encoding="utf-8") as f:
    f.write("order_id,customer_id,product_id,quantity,order_date\n")
    for r in clean_orders:
        f.write(",".join(str(x) for x in r) + "\n")

print(f"Generated {len(customers)} customers, {len(products)} products, {len(clean_orders)} orders")
print(f"Raw orders file has {len(dirty_orders)} rows (includes {len(dup_indices)} duplicates, 15 null quantities, 8 bad dates)")
