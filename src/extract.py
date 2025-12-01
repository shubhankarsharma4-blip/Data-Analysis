"""
Extract phase: Load raw CSV files.
Handles errors gracefully and logs detailed information about data loaded.
"""
import pandas as pd
from pathlib import Path
from . import config
from .logger_config import get_logger, log_context

logger = get_logger(__name__)


def load_csv_safe(filepath: Path, table_name: str) -> pd.DataFrame:
    """
    Safely load a CSV file with error handling.
    
    Args:
        filepath: Path to CSV file
        table_name: Name of the table (for logging)
    
    Returns:
        DataFrame or empty DataFrame if file not found
    
    Raises:
        Exception: If CSV is corrupted or unreadable (after logging)
    """
    try:
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return pd.DataFrame()
        
        df = pd.read_csv(filepath)
        logger.debug(f"  Loaded {table_name}: {filepath}")
        return df
    
    except pd.errors.ParserError as e:
        logger.error(f"CSV parsing error in {table_name}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading {table_name}: {type(e).__name__}: {e}")
        raise


def load_users():
    """Load users table with error handling and logging."""
    with log_context(logger, "load_users", source="users.csv"):
        df = load_csv_safe(config.USERS_CSV, "users")
        logger.info(f"✓ Loaded {len(df)} users")
        return df


def load_products():
    """Load products table with error handling and logging."""
    with log_context(logger, "load_products", source="products.csv"):
        df = load_csv_safe(config.PRODUCTS_CSV, "products")
        logger.info(f"✓ Loaded {len(df)} products")
        return df


def load_orders():
    """Load orders table with error handling and logging."""
    with log_context(logger, "load_orders", source="orders.csv"):
        df = load_csv_safe(config.ORDERS_CSV, "orders")
        logger.info(f"✓ Loaded {len(df)} orders")
        return df


def load_order_items():
    """Load order items table with error handling and logging."""
    with log_context(logger, "load_order_items", source="order_items.csv"):
        df = load_csv_safe(config.ORDER_ITEMS_CSV, "order_items")
        logger.info(f"✓ Loaded {len(df)} order items")
        return df


def load_events():
    """Load events table with error handling and logging."""
    with log_context(logger, "load_events", source="events.csv"):
        df = load_csv_safe(config.EVENTS_CSV, "events")
        logger.info(f"✓ Loaded {len(df)} events")
        return df


def load_reviews():
    """Load reviews table with error handling and logging."""
    with log_context(logger, "load_reviews", source="reviews.csv"):
        df = load_csv_safe(config.REVIEWS_CSV, "reviews")
        logger.info(f"✓ Loaded {len(df)} reviews")
        return df


def load_all_raw():
    """
    Load all raw tables with comprehensive error handling.
    Logs entry/exit and summary statistics.
    """
    logger.info("=" * 60)
    logger.info("EXTRACT PHASE: Loading all raw CSV files")
    logger.info("=" * 60)
    
    try:
        raw_data = {
            "users": load_users(),
            "products": load_products(),
            "orders": load_orders(),
            "order_items": load_order_items(),
            "events": load_events(),
            "reviews": load_reviews(),
        }
        
        # Log summary statistics
        logger.info("\nExtract Summary:")
        for table_name, df in raw_data.items():
            total_rows = len(df)
            total_cols = len(df.columns)
            null_count = df.isnull().sum().sum()
            if null_count > 0:
                logger.warning(f"  {table_name}: {total_rows} rows × {total_cols} cols | {null_count} NULL values found")
            else:
                logger.debug(f"  {table_name}: {total_rows} rows × {total_cols} cols")
        
        logger.info("Extract phase completed successfully")
        return raw_data
    
    except Exception as e:
        logger.error(f"Extract phase failed: {type(e).__name__}: {e}", exc_info=True)
        raise
