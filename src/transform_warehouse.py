"""
Transform Warehouse Phase: Build dimensional and fact tables.
Logs all table builds with row counts and data quality metrics.
"""
import pandas as pd
from .logger_config import get_logger, log_context

logger = get_logger(__name__)


def build_dim_users(stg_users: pd.DataFrame) -> pd.DataFrame:
    """Build users dimension with derived columns."""
    with log_context(logger, "build_dim_users"):
        df = stg_users.copy()
        
        # Add derived columns
        df['signup_year'] = df['signup_date'].dt.year
        df['signup_month'] = df['signup_date'].dt.month
        
        logger.debug(f"  Added signup_year and signup_month columns")
        logger.info(f"  dim_users: {len(df)} rows × {len(df.columns)} columns")
        return df


def build_dim_products(stg_products: pd.DataFrame) -> pd.DataFrame:
    """Build products dimension."""
    with log_context(logger, "build_dim_products"):
        df = stg_products.copy()
        logger.info(f"  dim_products: {len(df)} rows × {len(df.columns)} columns")
        return df


def build_fact_orders(stg_orders: pd.DataFrame) -> pd.DataFrame:
    """Build orders fact table."""
    with log_context(logger, "build_fact_orders"):
        df = stg_orders.copy()
        logger.info(f"  fact_orders: {len(df)} rows × {len(df.columns)} columns")
        return df


def build_fact_order_items(stg_order_items: pd.DataFrame) -> pd.DataFrame:
    """Build order items fact table with calculated totals."""
    with log_context(logger, "build_fact_order_items"):
        df = stg_order_items.copy()
        
        # Calculate missing item totals
        if 'item_total' in df.columns:
            missing_total = df['item_total'].isna()
            count_missing = missing_total.sum()
            if count_missing > 0:
                logger.warning(f"  {count_missing} missing item_total values - calculating from quantity × price")
                df.loc[missing_total, 'item_total'] = (
                    df.loc[missing_total, 'quantity'] * 
                    df.loc[missing_total, 'item_price']
                )
        else:
            logger.info(f"  Creating item_total column from quantity × price")
            df['item_total'] = df['quantity'] * df['item_price']
        
        logger.info(f"  fact_order_items: {len(df)} rows × {len(df.columns)} columns")
        return df


def build_fact_events(stg_events: pd.DataFrame) -> pd.DataFrame:
    """Build events fact table with derived date/time columns."""
    with log_context(logger, "build_fact_events"):
        df = stg_events.copy()
        
        # Add derived time columns
        df['event_date'] = df['event_timestamp'].dt.date
        df['event_hour'] = df['event_timestamp'].dt.hour
        
        logger.debug(f"  Added event_date and event_hour columns")
        logger.info(f"  fact_events: {len(df)} rows × {len(df.columns)} columns")
        return df


def build_fact_reviews(stg_reviews: pd.DataFrame) -> pd.DataFrame:
    """Build reviews fact table."""
    with log_context(logger, "build_fact_reviews"):
        df = stg_reviews.copy()
        logger.info(f"  fact_reviews: {len(df)} rows × {len(df.columns)} columns")
        return df


def build_warehouse(stg: dict) -> dict:
    """Build all dimension and fact tables with error handling."""
    logger.info("=" * 60)
    logger.info("TRANSFORM WAREHOUSE PHASE: Building dimensions and facts")
    logger.info("=" * 60)
    
    try:
        warehouse = {
            "dim_users": build_dim_users(stg["users"]),
            "dim_products": build_dim_products(stg["products"]),
            "fact_orders": build_fact_orders(stg["orders"]),
            "fact_order_items": build_fact_order_items(stg["order_items"]),
            "fact_events": build_fact_events(stg["events"]),
            "fact_reviews": build_fact_reviews(stg["reviews"]),
        }
        
        # Summary statistics
        logger.info("\nWarehouse Summary:")
        total_rows = sum(len(df) for df in warehouse.values())
        logger.info(f"  Total rows across all tables: {total_rows:,}")
        
        logger.info("Transform warehouse phase completed successfully")
        return warehouse
    
    except Exception as e:
        logger.error(f"Transform warehouse phase failed: {type(e).__name__}: {e}", exc_info=True)
        raise
