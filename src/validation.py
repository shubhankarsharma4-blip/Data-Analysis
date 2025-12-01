"""
Data validation and quality checks for ETL pipeline.
Validates processed tables against business rules and data integrity constraints.
"""
import pandas as pd
from pathlib import Path
from .logger_config import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Raised when data validation fails."""
    pass


def check_null_primary_keys(tables: dict) -> dict:
    """
    Verify that primary keys have no NULL values.
    Returns dict with table names and null counts.
    """
    logger.info("Validating primary keys for NULL values...")
    results = {}
    
    pk_map = {
        "dim_users": "user_id",
        "dim_products": "product_id",
        "fact_orders": "order_id",
        "fact_order_items": "order_item_id",
        "fact_events": "event_id",
        "fact_reviews": "review_id",
    }
    
    for table_name, pk_col in pk_map.items():
        if table_name not in tables:
            continue
        
        df = tables[table_name]
        if pk_col not in df.columns:
            logger.warning(f"  {table_name}: primary key '{pk_col}' not found in table")
            results[table_name] = -1
            continue
        
        null_count = df[pk_col].isna().sum()
        results[table_name] = null_count
        
        if null_count > 0:
            logger.error(f"  ❌ {table_name}: {null_count} NULL values in primary key '{pk_col}'")
        else:
            logger.info(f"  ✓ {table_name}: primary key has no NULL values")
    
    return results


def check_referential_integrity(tables: dict) -> dict:
    """
    Verify referential integrity: foreign keys reference existing primary keys.
    """
    logger.info("Validating referential integrity...")
    results = {}
    
    # Define foreign key relationships
    fk_rules = [
        {
            "child_table": "fact_orders",
            "fk_column": "user_id",
            "parent_table": "dim_users",
            "pk_column": "user_id",
        },
        {
            "child_table": "fact_order_items",
            "fk_column": "order_id",
            "parent_table": "fact_orders",
            "pk_column": "order_id",
        },
        {
            "child_table": "fact_order_items",
            "fk_column": "product_id",
            "parent_table": "dim_products",
            "pk_column": "product_id",
        },
        {
            "child_table": "fact_events",
            "fk_column": "user_id",
            "parent_table": "dim_users",
            "pk_column": "user_id",
        },
        {
            "child_table": "fact_reviews",
            "fk_column": "product_id",
            "parent_table": "dim_products",
            "pk_column": "product_id",
        },
    ]
    
    for rule in fk_rules:
        child = rule["child_table"]
        parent = rule["parent_table"]
        fk = rule["fk_column"]
        pk = rule["pk_column"]
        
        if child not in tables or parent not in tables:
            logger.warning(f"  Skipping {child}.{fk} → {parent}.{pk} (table not found)")
            continue
        
        child_df = tables[child]
        parent_df = tables[parent]
        
        if fk not in child_df.columns or pk not in parent_df.columns:
            logger.warning(f"  Skipping {child}.{fk} → {parent}.{pk} (column not found)")
            continue
        
        # Check for orphaned records
        child_fk_values = child_df[fk].dropna().unique()
        parent_pk_values = parent_df[pk].unique()
        
        orphaned = set(child_fk_values) - set(parent_pk_values)
        orphan_count = len(orphaned)
        
        key = f"{child}.{fk} → {parent}.{pk}"
        results[key] = orphan_count
        
        if orphan_count > 0:
            logger.error(f"  ❌ {key}: {orphan_count} orphaned records found")
        else:
            logger.info(f"  ✓ {key}: all foreign keys are valid")
    
    return results


def check_date_ranges(tables: dict) -> dict:
    """
    Verify that date columns are within reasonable ranges (no future dates, etc.).
    """
    logger.info("Validating date ranges (no future dates)...")
    results = {}
    
    date_columns = {
        "dim_users": "signup_date",
        "fact_orders": "order_date",
        "fact_events": "event_timestamp",
        "fact_reviews": "review_date",
    }
    
    from datetime import datetime
    today = pd.Timestamp(datetime.now().date())
    
    for table_name, date_col in date_columns.items():
        if table_name not in tables:
            continue
        
        df = tables[table_name]
        if date_col not in df.columns:
            logger.warning(f"  {table_name}: date column '{date_col}' not found")
            results[table_name] = -1
            continue
        
        # Convert to datetime if not already
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Check for future dates
        future_dates = (df[date_col] > today).sum()
        results[table_name] = future_dates
        
        if future_dates > 0:
            logger.error(f"  ❌ {table_name}: {future_dates} records with future dates in '{date_col}'")
        else:
            logger.info(f"  ✓ {table_name}: all dates are within valid range")
    
    return results


def check_numeric_ranges(tables: dict) -> dict:
    """
    Verify that numeric columns are within reasonable ranges.
    """
    logger.info("Validating numeric ranges (no negative prices/amounts)...")
    results = {}
    
    checks = [
        ("dim_products", "price", lambda x: x >= 0),
        ("fact_orders", "total_amount", lambda x: x >= 0),
        ("fact_order_items", "quantity", lambda x: x > 0),
        ("fact_order_items", "item_price", lambda x: x >= 0),
    ]
    
    for table_name, col, condition in checks:
        if table_name not in tables:
            continue
        
        df = tables[table_name]
        if col not in df.columns:
            logger.warning(f"  {table_name}: column '{col}' not found")
            continue
        
        df[col] = pd.to_numeric(df[col], errors='coerce')
        invalid_count = (~condition(df[col]) & df[col].notna()).sum()
        
        key = f"{table_name}.{col}"
        results[key] = invalid_count
        
        if invalid_count > 0:
            logger.error(f"  ❌ {key}: {invalid_count} invalid values (outside valid range)")
        else:
            logger.info(f"  ✓ {key}: all values are within valid range")
    
    return results


def validate_all(tables: dict, fail_on_error: bool = False) -> bool:
    """
    Run all validation checks on processed tables.
    
    Args:
        tables: Dictionary of table name → DataFrame
        fail_on_error: If True, raise exception on any validation failure
    
    Returns:
        True if all checks pass, False if any check fails
    """
    logger.info("\n" + "=" * 60)
    logger.info("DATA QUALITY VALIDATION")
    logger.info("=" * 60)
    
    all_passed = True
    
    try:
        pk_results = check_null_primary_keys(tables)
        if any(count > 0 for count in pk_results.values() if count >= 0):
            all_passed = False
    except Exception as e:
        logger.error(f"Primary key validation failed: {e}")
        all_passed = False
    
    try:
        fk_results = check_referential_integrity(tables)
        if any(count > 0 for count in fk_results.values()):
            all_passed = False
    except Exception as e:
        logger.error(f"Referential integrity validation failed: {e}")
        all_passed = False
    
    try:
        date_results = check_date_ranges(tables)
        if any(count > 0 for count in date_results.values() if count >= 0):
            all_passed = False
    except Exception as e:
        logger.error(f"Date range validation failed: {e}")
        all_passed = False
    
    try:
        numeric_results = check_numeric_ranges(tables)
        if any(count > 0 for count in numeric_results.values()):
            all_passed = False
    except Exception as e:
        logger.error(f"Numeric range validation failed: {e}")
        all_passed = False
    
    logger.info("=" * 60)
    if all_passed:
        logger.info("✅ ALL VALIDATION CHECKS PASSED")
    else:
        logger.warning("⚠️  SOME VALIDATION CHECKS FAILED - Review logs above")
    logger.info("=" * 60 + "\n")
    
    if fail_on_error and not all_passed:
        raise ValidationError("Data validation failed. Check logs for details.")
    
    return all_passed


def load_processed_tables(processed_dir: Path) -> dict:
    """
    Load all processed CSV files from the processed directory.
    """
    logger.info(f"Loading processed tables from {processed_dir}")
    
    tables = {}
    csv_files = processed_dir.glob("*.csv")
    
    for csv_file in csv_files:
        table_name = csv_file.stem
        df = pd.read_csv(csv_file)
        tables[table_name] = df
        logger.debug(f"  Loaded {table_name}: {len(df)} rows")
    
    logger.info(f"✓ Loaded {len(tables)} tables")
    return tables
