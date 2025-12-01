"""
Main ETL Pipeline Orchestrator.
Coordinates extract, transform, and load stages with comprehensive error handling.
"""
from . import extract, transform_staging, transform_warehouse, load, config
from .logger_config import get_logger

logger = get_logger(__name__)


def run_pipeline():
    """
    Execute the complete ETL pipeline with error handling.
    
    Stages:
    1. Extract: Load raw data from CSV files
    2. Transform Staging: Clean and standardize data
    3. Transform Warehouse: Build dimensional and fact tables
    4. Load: Save processed data to CSV files
    
    Raises:
        Exception: If any stage fails (with detailed logging)
    """
    try:
        logger.info("\n" + "=" * 60)
        logger.info("STARTING ETL PIPELINE")
        logger.info("=" * 60)
        
        # 1. Extract
        logger.info("\n→ STAGE 1: EXTRACT")
        raw = extract.load_all_raw()
        logger.info(f"✓ Extract complete: {len(raw)} tables loaded")

        # 2. Transform – staging/cleaning
        logger.info("\n→ STAGE 2: TRANSFORM STAGING")
        stg = transform_staging.stage_all(raw)
        logger.info(f"✓ Staging complete: {len(stg)} tables staged")

        # 3. Transform – warehouse: dims & facts
        logger.info("\n→ STAGE 3: TRANSFORM WAREHOUSE")
        wh = transform_warehouse.build_warehouse(stg)
        logger.info(f"✓ Warehouse build complete: {len(wh)} tables created")

        # 4. Load – save processed tables to CSV
        logger.info("\n→ STAGE 4: LOAD")
        load.save_as_csv(wh, config.PROCESSED_DIR)
        logger.info(f"✓ Load complete: All tables saved")

        logger.info("=" * 60)
        logger.info("✅ ETL PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"Processed tables saved in: {config.PROCESSED_DIR}")
        logger.info("=" * 60 + "\n")
        
    except KeyError as e:
        logger.error(f"❌ Data structure error (missing table/column): {e}", exc_info=True)
        raise
    
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {type(e).__name__}: {e}", exc_info=True)
        logger.error("Pipeline execution halted. Check logs above for details.")
        raise
