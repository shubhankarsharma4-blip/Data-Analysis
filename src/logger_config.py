"""
Logging configuration for ETL pipeline.
Logs to both console and file for audit trail and debugging.
Provides production-grade logging with error handling and context tracking.
"""
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

# Ensure logs directory exists
LOGS_DIR = Path(__file__).resolve().parents[1] / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Create log file with timestamp
LOG_FILE = LOGS_DIR / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    Logs to both console and file with structured format.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding duplicate handlers
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Formatter for all handlers - structured and readable
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (DEBUG level - more detailed for debugging)
    file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_log_file_path() -> Path:
    """Return the current log file path."""
    return LOG_FILE


@contextmanager
def log_context(logger: logging.Logger, context_name: str, **metadata):
    """
    Context manager for logging operations with entry/exit logging.
    
    Example:
        with log_context(logger, "loading_users", source="users.csv"):
            # Your code here
            pass
    
    Args:
        logger: Logger instance
        context_name: Name of the operation
        metadata: Additional context metadata to log
    """
    meta_str = " | ".join(f"{k}={v}" for k, v in metadata.items())
    prefix = f"[{context_name}]"
    
    try:
        logger.info(f"→ {prefix} Starting... {meta_str}" if meta_str else f"→ {prefix} Starting...")
        yield
        logger.info(f"✓ {prefix} Completed successfully")
    except Exception as e:
        logger.error(f"✗ {prefix} Failed with error: {type(e).__name__}: {e}", exc_info=True)
        raise


def log_summary(logger: logging.Logger, title: str, items: dict):
    """
    Log a summary table of items.
    
    Example:
        log_summary(logger, "Row Counts", {
            "users": 10000,
            "products": 2000,
            "orders": 20000,
        })
    
    Args:
        logger: Logger instance
        title: Summary title
        items: Dictionary of item_name -> value
    """
    logger.info(f"\n{title}")
    logger.info("─" * 60)
    for name, value in items.items():
        logger.info(f"  {name:.<40} {value:>15}")
    logger.info("─" * 60)

