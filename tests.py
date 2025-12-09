import pandas as pd
from pathlib import Path

df = pd.read_csv(Path("data/processed/dim_users.csv"))
print(df.columns)
