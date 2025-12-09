# to_sqlite.py
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

# Project root = folder where this file lives
PROJECT_ROOT = Path(__file__).resolve().parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DB_PATH = PROJECT_ROOT / "data" / "ecommerce_dw.db"

def load_table(name: str) -> pd.DataFrame:
    path = PROCESSED_DIR / f"{name}.csv"
    print(f"Loading {path} ...")
    return pd.read_csv(path)

def main():
    # Create data folder if missing
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Create SQLite engine
    engine = create_engine(f"sqlite:///{DB_PATH}")
    print("Writing to database:", DB_PATH)

    tables = [
        "dim_users",
        "dim_products",
        "fact_orders",
        "fact_order_items",
        "fact_events",
        "fact_reviews",
    ]

    for t in tables:
        df = load_table(t)
        df.to_sql(t, engine, if_exists="replace", index=False)
        print(f"→ {t} written ({df.shape[0]} rows)")

    print("✅ Database created at:", DB_PATH)

if __name__ == "__main__":
    main()
