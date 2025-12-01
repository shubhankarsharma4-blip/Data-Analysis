"""
Transform Staging Phase: Clean and standardize raw data.
Logs all transformations, dropped rows, and data quality warnings.
"""
import pandas as pd
from .logger_config import get_logger, log_context

logger = get_logger(__name__)


def stage_users(df_users: pd.DataFrame) -> pd.DataFrame:
    """Stage users: convert dates, normalize text, remove duplicates."""
    with log_context(logger, "stage_users"):
        df = df_users.copy()
        before_count = len(df)
        
        # Track transformations
        null_user_ids = df['user_id'].isna().sum()
        if null_user_ids > 0:
            logger.warning(f"  Found {null_user_ids} NULL user_ids (will cause issues)")
        
        df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
        bad_dates = df['signup_date'].isna().sum()
        if bad_dates > 0:
            logger.warning(f"  {bad_dates} invalid signup dates converted to NaT")
        
        df['gender'] = df['gender'].astype(str).str.strip().str.title()
        df['city'] = df['city'].astype(str).str.strip()
        
        before_dedup = len(df)
        df = df.drop_duplicates(subset='user_id')
        dropped = before_dedup - len(df)
        
        logger.info(f"  Users: {before_count} → {len(df)} rows (dropped {dropped} duplicates)")
        return df


def stage_products(df_products: pd.DataFrame) -> pd.DataFrame:
    """Stage products: convert numeric types, normalize text, remove duplicates."""
    with log_context(logger, "stage_products"):
        df = df_products.copy()
        before_count = len(df)
        
        null_product_ids = df['product_id'].isna().sum()
        if null_product_ids > 0:
            logger.warning(f"  Found {null_product_ids} NULL product_ids (will cause issues)")
        
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        bad_prices = df['price'].isna().sum()
        if bad_prices > 0:
            logger.warning(f"  {bad_prices} invalid prices converted to NaN")
        
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        
        df['category'] = df['category'].astype(str).str.strip()
        df['brand'] = df['brand'].astype(str).str.strip()
        
        before_dedup = len(df)
        df = df.drop_duplicates(subset='product_id')
        dropped = before_dedup - len(df)
        
        logger.info(f"  Products: {before_count} → {len(df)} rows (dropped {dropped} duplicates)")
        return df


def stage_orders(df_orders: pd.DataFrame) -> pd.DataFrame:
    """Stage orders: convert dates and numerics, normalize text, remove duplicates."""
    with log_context(logger, "stage_orders"):
        df = df_orders.copy()
        before_count = len(df)
        
        null_order_ids = df['order_id'].isna().sum()
        if null_order_ids > 0:
            logger.warning(f"  Found {null_order_ids} NULL order_ids (will cause issues)")
        
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        bad_dates = df['order_date'].isna().sum()
        if bad_dates > 0:
            logger.warning(f"  {bad_dates} invalid order dates converted to NaT")
        
        df['order_status'] = df['order_status'].astype(str).str.strip().str.lower()
        df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
        bad_amounts = df['total_amount'].isna().sum()
        if bad_amounts > 0:
            logger.warning(f"  {bad_amounts} invalid amounts converted to NaN")
        
        before_dedup = len(df)
        df = df.drop_duplicates(subset='order_id')
        dropped = before_dedup - len(df)
        
        logger.info(f"  Orders: {before_count} → {len(df)} rows (dropped {dropped} duplicates)")
        return df


def stage_order_items(df_order_items: pd.DataFrame) -> pd.DataFrame:
    """Stage order items: convert numerics, calculate totals, remove duplicates."""
    with log_context(logger, "stage_order_items"):
        df = df_order_items.copy()
        before_count = len(df)
        
        null_order_item_ids = df['order_item_id'].isna().sum()
        if null_order_item_ids > 0:
            logger.warning(f"  Found {null_order_item_ids} NULL order_item_ids (will cause issues)")
        
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
        df['item_price'] = pd.to_numeric(df['item_price'], errors='coerce')
        
        bad_qty = df['quantity'].isna().sum()
        bad_price = df['item_price'].isna().sum()
        if bad_qty > 0 or bad_price > 0:
            logger.warning(f"  {bad_qty} bad quantities, {bad_price} bad prices")
        
        if 'item_total' in df.columns:
            df['item_total'] = pd.to_numeric(df['item_total'], errors='coerce')
        
        before_dedup = len(df)
        df = df.drop_duplicates(subset='order_item_id')
        dropped = before_dedup - len(df)
        
        logger.info(f"  Order Items: {before_count} → {len(df)} rows (dropped {dropped} duplicates)")
        return df


def stage_events(df_events: pd.DataFrame) -> pd.DataFrame:
    """Stage events: convert timestamps, normalize event types, remove duplicates."""
    with log_context(logger, "stage_events"):
        df = df_events.copy()
        before_count = len(df)
        
        null_event_ids = df['event_id'].isna().sum()
        if null_event_ids > 0:
            logger.warning(f"  Found {null_event_ids} NULL event_ids (will cause issues)")
        
        df['event_timestamp'] = pd.to_datetime(df['event_timestamp'], errors='coerce')
        bad_ts = df['event_timestamp'].isna().sum()
        if bad_ts > 0:
            logger.warning(f"  {bad_ts} invalid timestamps converted to NaT")
        
        df['event_type'] = df['event_type'].astype(str).str.strip().str.lower()
        
        before_dedup = len(df)
        df = df.drop_duplicates(subset='event_id')
        dropped = before_dedup - len(df)
        
        logger.info(f"  Events: {before_count} → {len(df)} rows (dropped {dropped} duplicates)")
        return df


def stage_reviews(df_reviews: pd.DataFrame) -> pd.DataFrame:
    """Stage reviews: convert ratings and dates, remove duplicates."""
    with log_context(logger, "stage_reviews"):
        df = df_reviews.copy()
        before_count = len(df)
        
        null_review_ids = df['review_id'].isna().sum()
        if null_review_ids > 0:
            logger.warning(f"  Found {null_review_ids} NULL review_ids (will cause issues)")
        
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        bad_ratings = df['rating'].isna().sum()
        if bad_ratings > 0:
            logger.warning(f"  {bad_ratings} invalid ratings converted to NaN")
        
        df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
        bad_dates = df['review_date'].isna().sum()
        if bad_dates > 0:
            logger.warning(f"  {bad_dates} invalid review dates converted to NaT")
        
        before_dedup = len(df)
        df = df.drop_duplicates(subset='review_id')
        dropped = before_dedup - len(df)
        
        logger.info(f"  Reviews: {before_count} → {len(df)} rows (dropped {dropped} duplicates)")
        return df


def stage_all(raw: dict) -> dict:
    """Apply staging transformations to all raw tables with error handling."""
    logger.info("=" * 60)
    logger.info("TRANSFORM STAGING PHASE: Cleaning and standardizing data")
    logger.info("=" * 60)
    
    try:
        staged = {
            "users": stage_users(raw["users"]),
            "products": stage_products(raw["products"]),
            "orders": stage_orders(raw["orders"]),
            "order_items": stage_order_items(raw["order_items"]),
            "events": stage_events(raw["events"]),
            "reviews": stage_reviews(raw["reviews"]),
        }
        
        logger.info("Transform staging phase completed successfully")
        return staged
    
    except Exception as e:
        logger.error(f"Transform staging phase failed: {type(e).__name__}: {e}", exc_info=True)
        raise
