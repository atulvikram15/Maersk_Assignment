# file: data_cleaning.py
import os
import pandas as pd

# === SETUP ===
BASE_DIR = r""
DATA_DIR = os.path.join(BASE_DIR, "data")
CLEAN_DIR = os.path.join(BASE_DIR, "cleaned_data2")

os.makedirs(CLEAN_DIR, exist_ok=True)

print(f"📂 Loading CSV files from: {DATA_DIR}")
print(f"🧹 Cleaned files will be saved to: {CLEAN_DIR}\n")

# === LOAD ALL TABLES ===
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
for name, fname in tables.items():
    path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(path):
        print(f"⚠️ Warning: {fname} not found.")
        continue
    dfs[name] = pd.read_csv(path)
    print(f"✅ Loaded {name}: {dfs[name].shape[0]} rows, {dfs[name].shape[1]} columns")

# ============================================================
# 🧼 LIGHT CLEANING STEPS — REMOVE DUPLICATES, FIX DATES ONLY
# ============================================================

# === 1. GEOLOCATION: Drop exact duplicate rows (considering all columns) ===
if "geolocation" in dfs:
    before = dfs["geolocation"].shape[0]
    dfs["geolocation"] = dfs["geolocation"].drop_duplicates()  # all columns checked
    after = dfs["geolocation"].shape[0]
    removed = before - after
    print(f"🌍 Geolocation: removed {removed} exact duplicate rows across all columns.")

# === 2. ORDERS: Convert date columns to datetime ===
if "orders" in dfs:
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in date_cols:
        if col in dfs["orders"].columns:
            dfs["orders"][col] = pd.to_datetime(dfs["orders"][col], errors="coerce")
    print("🕒 Orders: converted timestamp columns to datetime objects.")

# === 3. TRANSLATIONS: Add 2 missing category translations (optional small fix) ===
if "product_category_translation" in dfs:
    trans = dfs["product_category_translation"]
    missing_rows = pd.DataFrame(
        {
            "product_category_name": [
                "portateis_cozinha_e_preparadores_de_alimentos",
                "pc_gamer",
            ],
            "product_category_name_english": [
                "portable_kitchen_appliances",
                "pc_gamer",
            ],
        }
    )
    trans = pd.concat([trans, missing_rows], ignore_index=True)
    dfs["product_category_translation"] = trans
    print("🈶 Added 2 missing product category translations.")

# ============================================================
# 💾 SAVE CLEANED FILES
# ============================================================
for name, df in dfs.items():
    save_path = os.path.join(CLEAN_DIR, tables[name])
    df.to_csv(save_path, index=False)
    print(f"💾 Saved cleaned {name} → {save_path}")

print("\n✅ Light data cleaning complete! All cleaned CSVs are saved in:")
print(CLEAN_DIR)
