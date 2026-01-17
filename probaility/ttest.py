from scipy.stats import ttest_1samp
import pandas as pd
import numpy as np

FILES = [
    "csvfile/pro/tatapower_2020_2025_daily_trend_trades.csv",
    "csvfile/pro/tatapower_2020_2025_daily_sideways_trades.csv",
    "csvfile/pro/infy_2020_2025_daily_trend_trades.csv",
    "csvfile/pro/infy_2020_2025_daily_sideways_trades.csv",
    "csvfile/pro/itc_2020_2025_daily_trend_trades.csv",
    "csvfile/pro/itc_2020_2025_daily_sideways_trades.csv",
]

def analyze(file):
    df = pd.read_csv(file)
    r = df["return"].dropna().values

    mean = np.mean(r)
    t, p = ttest_1samp(r, 0)

    print("\n", file.split("/")[-1])
    print("Trades:", len(r))
    print("Mean:", round(mean*100, 4), "%")
    print("T:", round(t, 4), " P:", round(p, 6))

    if p < 0.05:
        print("✅ REAL EDGE")
    else:
        print("❌ NO EDGE")

for f in FILES:
    analyze(f)
