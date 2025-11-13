"""
load_olist_sqlalchemy.py
- Requires: pandas, sqlalchemy, pymysql
- Usage: python load_olist_sqlalchemy.py
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# ---------- CONFIG ----------
DB_USER = ""
DB_PASS = ""
DB_HOST = ""
DB_PORT = 3306
DB_NAME = ""

CSV_DIR = r"C:\Users\atul\python_programs\cleaned_data2"   # <- change to folder containing all CSV files
# Ensure CSV filenames match these names (as downloaded from Kaggle)
FILES = {
    #"customers": "olist_customers_dataset.csv",
    #"geolocation": "olist_geolocation_dataset.csv",
    #"sellers": "olist_sellers_dataset.csv",
    #"products": "olist_products_dataset.csv",
    #"category_translation": "product_category_name_translation.csv",
    #"orders": "olist_orders_dataset.csv",
    #"order_items": "olist_order_items_dataset.csv",
    #"order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv"
}
# Chunk size for large CSVs
CHUNK_SIZE = 20000

# ---------- CONNECT ----------
uri = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(uri, pool_pre_ping=True)

# ---------- Run SQL schema file first ----------
def run_schema(sql_file_path: str):
    with open(sql_file_path, "r", encoding="utf8") as f:
        sql = f.read()
    with engine.connect() as conn:
        for statement in sql.split(";"):
            stmt = statement.strip()
            if not stmt:
                continue
            conn.execute(text(stmt))
        conn.commit()
    print("Schema executed.")

# ---------- Helper: parse datetimes & dtypes per table ----------
PARSERS = {
    "orders": {
        "parse_dates": [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
    },
    "order_items": {"parse_dates": ["shipping_limit_date"]},
    "order_reviews": {"parse_dates": ["review_creation_date", "review_answer_timestamp"]},
    # other files don't need date parsing
}

DTYPES = {
    "customers": {
        "customer_id": "string",
        "customer_unique_id": "string",
        "customer_zip_code_prefix": "Int64",
        "customer_city": "string",
        "customer_state": "string"
    },
    "geolocation": {
        "geolocation_zip_code_prefix": "Int64",
        "geolocation_lat": "float",
        "geolocation_lng": "float",
        "geolocation_city": "string",
        "geolocation_state": "string"
    },
    "sellers": {
        "seller_id": "string",
        "seller_zip_code_prefix": "Int64",
        "seller_city": "string",
        "seller_state": "string"
    },
    "products": {
        "product_id": "string",
        "product_category_name": "string",
        "product_name_length": "Int64",
        "product_description_length": "Int64",
        "product_photos_qty": "Int64",
        "product_weight_g": "Int64",
        "product_length_cm": "Int64",
        "product_height_cm": "Int64",
        "product_width_cm": "Int64"
    },
    "category_translation": {
        "product_category_name": "string",
        "product_category_name_english": "string"
    },
    "order_items": {
        "order_id": "string",
        "order_item_id": "Int64",
        "product_id": "string",
        "seller_id": "string",
        "price": "float",
        "freight_value": "float"
    },
    "order_payments": {
        "order_id": "string",
        "payment_sequential": "Int64",
        "payment_type": "string",
        "payment_installments": "Int64",
        "payment_value": "float"
    },
    "order_reviews": {
        "review_id": "string",
        "order_id": "string",
        "review_score": "Int64",
        "review_comment_title": "string",
        "review_comment_message": "string"
    },
    "orders": {
        "order_id": "string",
        "customer_id": "string",
        "order_status": "string"
    }
}

# ---------- Load CSV to SQL (create tables already created by schema) ----------
def load_table(table_key: str, csv_path: str):
    print(f"\n=== Loading {table_key} from {csv_path}")
    parse_dates = PARSERS.get(table_key, {}).get("parse_dates", None)
    dtype = DTYPES.get(table_key, None)

    # some files are big -> use chunking
    try:
        if os.path.getsize(csv_path) > 5_000_000:  # > 5 MB -> chunk
            it = pd.read_csv(csv_path, dtype=dtype, parse_dates=parse_dates, chunksize=CHUNK_SIZE, low_memory=False)
            for i, chunk in enumerate(it):
                # optional: small cleanup
                chunk = chunk.where(pd.notnull(chunk), None)
                chunk.to_sql(table_key, con=engine, if_exists="append", index=False, method="multi")
                print(f"  chunk {i+1} appended ({len(chunk)} rows)")
        else:
            df = pd.read_csv(csv_path, dtype=dtype, parse_dates=parse_dates, low_memory=False)
            df = df.where(pd.notnull(df), None)
            df.to_sql(table_key, con=engine, if_exists="append", index=False, method="multi")
            print(f"  appended {len(df)} rows (single chunk).")
    except SQLAlchemyError as e:
        print("SQLAlchemy error:", e)
        #raise
        pass
    except Exception as e:
        print("Error loading:", e)
        #raise
        pass

def main():
    sql_file = os.path.join(os.path.dirname(__file__), "olist_schema.sql")
    print("Running schema...")
    run_schema(sql_file)

    # load order: parents first (customers, products, sellers), then orders, then dependent tables
    order = [
        #"customers",
        #"geolocation",
        #"sellers",
        #"products",
        #"category_translation",
        #"orders",
        #"order_items",
        #"order_payments",
        "order_reviews"
    ]

    for table in order:
        csv_name = FILES[table]
        csv_path = os.path.join(CSV_DIR, csv_name)
        if not os.path.exists(csv_path):
            print(f"  SKIP: {csv_path} not found. Place CSVs in {CSV_DIR} or update FILES dict.")
            continue
        
        load_table(table, csv_path)
        

    print("\nAll done.")

if __name__ == "__main__":
    main()
