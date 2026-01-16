import yfinance as yf
import pandas as pd
import os
from datetime import datetime

SYMBOL = "SAIL.NS"
SAVE_PATH = "data/csvfile/sail_2020_2025_daily.csv"

# Fetch INFY data from 2020 to Dec 31, 2025
df = yf.download(
    SYMBOL,
    start="2020-01-01",      # ✅ Start of 2020
    end="2025-12-31",        # ✅ End of 2025 (exclusive, so Dec 30 last trading day)
    interval="1d",           # ✅ Daily data
    auto_adjust=False,
    progress=False
)

# Reset index to get Date column
df.reset_index(inplace=True)

# Keep only required columns
df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

# Ensure directory exists
os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

# Save CSV
df.to_csv(SAVE_PATH, index=False)

print("✅ INFY 2020-2025 Daily data fetched successfully")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"Total rows: {len(df)}")
print("\nFirst 5 rows:")
print(df.head())
print("\nLast 5 rows:")
print(df.tail())
