"""
Load Phase: Save processed tables to CSV and database.
Logs all save operations with verification and error handling.
"""
from pathlib import Path
from .logger_config import get_logger, log_context

logger = get_logger(__name__)


def save_as_csv(tables: dict, output_dir: Path):
    """
    Save all processed tables to CSV files with error handling.
    
    Args:
        tables: Dictionary of table_name -> DataFrame
        output_dir: Output directory for CSV files
    
    Raises:
        Exception: If any save operation fails
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("=" * 60)
        logger.info("LOAD PHASE: Saving processed tables to CSV")
        logger.info("=" * 60)
        
        failed_saves = []
        
        for name, df in tables.items():
            try:
                filepath = output_dir / f"{name}.csv"
                
                if df is None or len(df) == 0:
                    logger.warning(f"  {name}: Empty DataFrame - skipping save")
                    continue
                
                df.to_csv(filepath, index=False)
                
                # Verify file was saved
                if not filepath.exists():
                    logger.error(f"  {name}: Save failed - file not created")
                    failed_saves.append(name)
                else:
                    file_size_kb = filepath.stat().st_size / 1024
                    logger.info(f"  ✓ {name}: {len(df)} rows → {filepath} ({file_size_kb:.1f} KB)")
                    logger.debug(f"    Columns: {', '.join(df.columns)}")
            
            except Exception as e:
                logger.error(f"  ✗ {name}: Save failed - {type(e).__name__}: {e}")
                failed_saves.append(name)
        
        if failed_saves:
            raise Exception(f"Failed to save tables: {', '.join(failed_saves)}")
        
        logger.info("Load phase completed successfully")
    
    except Exception as e:
        logger.error(f"Load phase failed: {type(e).__name__}: {e}", exc_info=True)
        raise
