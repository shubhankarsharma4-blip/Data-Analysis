"""
Master ETL Orchestrator Script

Runs the complete ETL pipeline in sequence:
1. Extract and transform raw data
2. Validate data quality
3. Load processed data into SQLite
4. Update state tracking for incremental loads

Usage:
    python run_all.py [--full] [--validate-only]

Args:
    --full:           Force full reload (ignore previous state)
    --validate-only:  Run validation on existing data without re-running pipeline
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import run_pipeline
from src.validation import validate_all, load_processed_tables
from src.config import PROCESSED_DIR
from src.incremental import update_run_timestamp, should_run_full_load
from src.logger_config import get_logger, get_log_file_path

logger = get_logger(__name__)


def load_to_sqlite():
    """
    Load processed CSV files into SQLite database.
    This is adapted from the notebook functionality.
    """
    logger.info("=" * 60)
    logger.info("LOADING DATA INTO SQLITE")
    logger.info("=" * 60)
    
    try:
        import pandas as pd
        from sqlalchemy import create_engine
        
        db_path = Path(__file__).parent / "ecommerce.db"
        engine = create_engine(f"sqlite:///{db_path}")
        
        logger.info(f"SQLite DB path: {db_path}")
        
        # Load and insert processed tables
        processed_dir = PROCESSED_DIR
        csv_files = list(processed_dir.glob("*.csv"))
        
        for csv_file in csv_files:
            table_name = csv_file.stem
            logger.info(f"Loading {table_name} into database...")
            
            df = pd.read_csv(csv_file)
            df.to_sql(table_name, con=engine, if_exists='replace', index=False)
            
            logger.info(f"  ✓ {table_name}: {len(df)} rows inserted")
        
        logger.info("✓ SQLite load completed")
        
    except ImportError as e:
        logger.error(f"Required package not found: {e}")
        logger.info("Skipping SQLite load. Install sqlalchemy and pandas to enable.")
    except Exception as e:
        logger.error(f"Failed to load data into SQLite: {e}", exc_info=True)
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Run complete ETL pipeline with validation and database load"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Force full reload (ignore previous state)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run validation on existing processed data without re-running pipeline"
    )
    
    args = parser.parse_args()
    
    logger.info("\n" + "=" * 70)
    logger.info("ETL ORCHESTRATOR - FULL PIPELINE RUN")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70 + "\n")
    
    try:
        # Step 1: Run ETL pipeline (unless validation-only)
        if not args.validate_only:
            logger.info(f"Full load: {args.full or should_run_full_load()}")
            run_pipeline()
        else:
            logger.info("Skipping pipeline (--validate-only mode)")
        
        # Step 2: Load processed data into SQLite
        if not args.validate_only:
            load_to_sqlite()
        
        # Step 3: Validate processed data
        logger.info("\nRunning data quality validation...")
        processed_tables = load_processed_tables(PROCESSED_DIR)
        validation_passed = validate_all(processed_tables, fail_on_error=False)
        
        # Step 4: Update state tracking
        if not args.validate_only:
            update_run_timestamp(table_states={})
        
        # Final summary
        logger.info("\n" + "=" * 70)
        if validation_passed:
            logger.info("✅ ETL PIPELINE COMPLETED SUCCESSFULLY")
        else:
            logger.warning("⚠️  PIPELINE COMPLETED WITH VALIDATION WARNINGS")
        logger.info(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Log file: {get_log_file_path()}")
        logger.info("=" * 70 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error("\n" + "=" * 70)
        logger.error("❌ ETL PIPELINE FAILED")
        logger.error(f"Error: {e}")
        logger.error(f"Log file: {get_log_file_path()}")
        logger.error("=" * 70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
