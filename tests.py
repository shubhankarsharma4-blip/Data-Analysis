import pandas as pd
from pathlib import Path

csv_path = Path(__file__).parent / "Data" / "Processed" / "dim_users.csv"

if csv_path.exists():
    df = pd.read_csv(csv_path)
    print(df.columns)
else:
    print(f"Missing file: {csv_path}")
