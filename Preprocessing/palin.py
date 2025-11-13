# file: data_quality_check.py
import os
import pandas as pd

# ✅ Absolute path to your dataset directory
DATA_DIR = r""

# Verify the directory
if not os.path.exists(DATA_DIR):
    raise FileNotFoundError(f"The directory {DATA_DIR} does not exist. Please check the path.")

# load each table
tables = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}

dfs = {}
print(f"Loading CSVs from: {DATA_DIR}\n")

for name, fname in tables.items():
    path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(path):
        print(f"⚠️ Warning: {fname} not found in {DATA_DIR}")
        continue
    dfs[name] = pd.read_csv(path)
    print(f"✅ Loaded {name}: {dfs[name].shape[0]} rows, {dfs[name].shape[1]} columns")
    print(f"   Columns: {list(dfs[name].columns)}\n")

# ==================== Data Quality Checks ====================

print("\n=== 🔍 Null / Missing Values by Table ===")
for name, df in dfs.items():
    null_counts = df.isnull().sum()
    nonzero = null_counts[null_counts > 0]
    print(f"\n📘 Table: {name}")
    if nonzero.empty:
        print("  ✅ No missing values.")
    else:
        print(nonzero.to_string())

print("\n=== 🔁 Duplicate Rows by Table ===")
for name, df in dfs.items():
    dup_count = df.duplicated().sum()
    print(f"📄 Table {name}: {dup_count} duplicate rows.")

print("\n=== 🧮 Data Type Summary for Key Tables ===")
for name in ["orders", "order_items", "products"]:
    if name in dfs:
        print(f"\n📘 Table: {name}")
        print(dfs[name].dtypes)

print("\n=== ⚙️ Example Inconsistencies: Products ↔ Category Translation ===")
if "products" in dfs and "product_category_translation" in dfs:
    prod = dfs["products"]
    trans = dfs["product_category_translation"]
    missing_cats = set(prod["product_category_name"].dropna().unique()) - set(trans["product_category_name"].dropna().unique())
    if len(missing_cats) == 0:
        print("✅ All product categories have translations.")
    else:
        print(f"⚠️ Missing translations for {len(missing_cats)} categories:")
        print(missing_cats)
else:
    print("⚠️ Either products or product_category_translation table missing.")
