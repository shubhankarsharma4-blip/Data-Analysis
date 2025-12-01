"""
Incremental load tracking and state management.
Tracks last run timestamp to support incremental data loads.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from .logger_config import get_logger

logger = get_logger(__name__)

# State file location
STATE_FILE = Path(__file__).resolve().parents[1] / ".etl_state.json"


def get_last_run_timestamp() -> Dict[str, Any]:
    """
    Load the last run state from disk.
    
    Returns:
        Dict with keys like 'last_run', 'orders_last_date', 'events_last_timestamp', etc.
    """
    if not STATE_FILE.exists():
        logger.info("No previous state found (first run)")
        return {"last_run": None, "tables": {}}
    
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        logger.debug(f"Loaded state from {STATE_FILE}")
        return state
    except Exception as e:
        logger.error(f"Failed to load state file: {e}")
        return {"last_run": None, "tables": {}}


def update_run_timestamp(table_states: Optional[Dict[str, Any]] = None):
    """
    Update the run state with current timestamp.
    
    Args:
        table_states: Optional dict with table-specific state (e.g., last processed dates)
    """
    now = datetime.now().isoformat()
    
    state = {
        "last_run": now,
        "tables": table_states or {},
    }
    
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"Updated state file with timestamp: {now}")
    except Exception as e:
        logger.error(f"Failed to update state file: {e}")


def get_incremental_filter(table_name: str, date_column: Optional[str] = None):
    """
    Get a filter to load only records newer than last run.
    
    Args:
        table_name: Name of the table (e.g., 'orders', 'events')
        date_column: Name of the date column to filter on
    
    Returns:
        Timestamp or None if first run
    """
    state = get_last_run_timestamp()
    
    if state["last_run"] is None:
        logger.info(f"  {table_name}: Full load (first run)")
        return None
    
    last_run = state["last_run"]
    table_state = state.get("tables", {}).get(table_name, {})
    last_processed = table_state.get("last_date")
    
    if last_processed:
        logger.info(f"  {table_name}: Incremental load since {last_processed}")
        return pd.Timestamp(last_processed)
    else:
        logger.info(f"  {table_name}: Full load (no prior state)")
        return None


def should_run_full_load() -> bool:
    """
    Determine if a full load should be run (first time or forced).
    """
    state = get_last_run_timestamp()
    return state["last_run"] is None


# Import pandas for timestamp operations
import pandas as pd
