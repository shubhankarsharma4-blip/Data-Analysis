"""
Initialization script for Streamlit Cloud deployment.
Runs the ETL pipeline once and saves data to both CSV and SQLite.
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src import extract, transform_staging, transform_warehouse, load, config

def initialize_for_streamlit():
    """Initialize all data for Streamlit Cloud"""
    print("Starting ETL pipeline initialization...")
    
    try:
        # 1. Extract
        print("→ Extracting raw data...")
        raw = extract.load_all_raw()
        print(f"✓ Extracted {len(raw)} raw tables")
        
        # 2. Transform Staging
        print("→ Staging and cleaning data...")
        stg = transform_staging.stage_all(raw)
        print(f"✓ Staged {len(stg)} tables")
        
        # 3. Transform Warehouse
        print("→ Building warehouse (dimensions & facts)...")
        wh = transform_warehouse.build_warehouse(stg)
        print(f"✓ Built {len(wh)} warehouse tables")
        
        # 4. Save as CSV
        print("→ Saving to CSV files...")
        load.save_as_csv(wh, config.PROCESSED_DIR)
        print(f"✓ Saved to {config.PROCESSED_DIR}")
        
        # 5. Save to SQLite
        print("→ Saving to SQLite database...")
        db_path = project_root / 'ecommerce.db'
        from sqlalchemy import create_engine
        engine = create_engine(f'sqlite:///{db_path}')
        
        for table_name, df in wh.items():
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"  ✓ {table_name}: {len(df)} rows")
        
        print(f"✓ Saved database to {db_path}")
        print("\n✅ Initialization complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = initialize_for_streamlit()
    sys.exit(0 if success else 1)
