from pathlib import Path

# Project root is the parent of this file's directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Raw CSV file paths
USERS_CSV       = RAW_DIR / "users.csv"
PRODUCTS_CSV    = RAW_DIR / "products.csv"
ORDERS_CSV      = RAW_DIR / "orders.csv"
ORDER_ITEMS_CSV = RAW_DIR / "order_items.csv"
EVENTS_CSV      = RAW_DIR / "events.csv"
REVIEWS_CSV     = RAW_DIR / "reviews.csv"

# Processed / output file paths
DIM_USERS_CSV         = PROCESSED_DIR / "dim_users.csv"
DIM_PRODUCTS_CSV      = PROCESSED_DIR / "dim_products.csv"
FACT_ORDERS_CSV       = PROCESSED_DIR / "fact_orders.csv"
FACT_ORDER_ITEMS_CSV  = PROCESSED_DIR / "fact_order_items.csv"
FACT_EVENTS_CSV       = PROCESSED_DIR / "fact_events.csv"
FACT_REVIEWS_CSV      = PROCESSED_DIR / "fact_reviews.csv"
