"""
Unit tests for ETL pipeline.
Run with: pytest tests/ -v
"""

import pytest
from pathlib import Path
import pandas as pd
from src.config import Config


@pytest.fixture
def config():
    """Provide Config object for tests."""
    return Config()


class TestFileStructure:
    """Test that required files and directories exist."""
    
    def test_raw_data_exists(self, config):
        """Test that raw data directory exists."""
        assert config.DATA_RAW_DIR.exists(), f"Raw data directory not found: {config.DATA_RAW_DIR}"
    
    def test_csv_files_exist(self, config):
        """Test that all required CSV files exist."""
        required_files = ["users.csv", "products.csv", "orders.csv", 
                         "order_items.csv", "events.csv", "reviews.csv"]
        for filename in required_files:
            filepath = config.DATA_RAW_DIR / filename
            assert filepath.exists(), f"Missing CSV file: {filename}"
    
    def test_src_module_exists(self):
        """Test that src module directory exists."""
        src_dir = Path(__file__).parent.parent / "src"
        assert src_dir.exists(), "src directory not found"


class TestDatabaseConfig:
    """Test database configuration."""
    
    def test_db_path_configured(self, config):
        """Test that database path is configured."""
        assert config.DB_PATH is not None, "Database path not configured"
        assert config.DB_PATH.name == "ecommerce.db", "Database name incorrect"


class TestLoggingConfig:
    """Test logging configuration."""
    
    def test_log_directory_exists(self, config):
        """Test that logs directory exists or can be created."""
        assert config.LOG_DIR is not None, "Log directory not configured"
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        assert config.LOG_DIR.exists(), "Could not create logs directory"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
