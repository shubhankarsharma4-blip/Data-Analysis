"""
Tests for extract module.
"""

import pytest
import pandas as pd
from pathlib import Path


class TestCSVLoading:
    """Test CSV loading functionality."""
    
    def test_csv_files_parseable(self):
        """Test that all CSV files can be parsed."""
        data_dir = Path(__file__).parent.parent / "Data" / "Raw"
        csv_files = ["users.csv", "products.csv", "orders.csv", 
                    "order_items.csv", "events.csv", "reviews.csv"]
        
        for filename in csv_files:
            filepath = data_dir / filename
            if filepath.exists():
                try:
                    df = pd.read_csv(filepath)
                    assert len(df) > 0, f"{filename} is empty"
                    assert len(df.columns) > 0, f"{filename} has no columns"
                except Exception as e:
                    pytest.fail(f"Failed to parse {filename}: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
