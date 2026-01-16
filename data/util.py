import pandas as pd
import numpy as np
import os

def build_features(csv_path):
    print(f"Processing: {csv_path}")

    # ================= LOAD =================
    df = pd.read_csv(csv_path)

    # ================= NUMERIC CLEAN =================
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna().reset_index(drop=True)

    # ================= DATE FIX =================
    if "Date" not in df.columns:
        df.reset_index(inplace=True)

    df["Date"] = pd.to_datetime(df["Date"])

    # ================= TIME FEATURES =================
    df["weekday"] = df["Date"].dt.weekday
    df["is_monday"] = (df["weekday"] == 0).astype(int)
    df["is_friday"] = (df["weekday"] == 4).astype(int)
    df["week"] = df["Date"].dt.isocalendar().week.astype(int)
    df["year"] = df["Date"].dt.year

    # ================= SMA (PRICE) =================
    df["sma_20"] = df["Close"].rolling(window=20).mean()
    df["sma_50"] = df["Close"].rolling(window=50).mean()

    # ================= EMA =================
    df["ema_50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["ema_200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # ================= RSI (WILDER) =================
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # ================= ATR =================
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.ewm(alpha=1/14, adjust=False).mean()

    # ================= ADX =================
    plus_dm = df["High"].diff()
    minus_dm = df["Low"].diff()

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = (-minus_dm).where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    plus_di = 100 * (plus_dm.ewm(alpha=1/14, adjust=False).mean() / df["atr"])
    minus_di = 100 * (minus_dm.ewm(alpha=1/14, adjust=False).mean() / df["atr"])

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df["adx"] = dx.ewm(alpha=1/14, adjust=False).mean()
    df["adx_prev"] = df["adx"].shift(1)

    # ================= VOLUME FILTER =================
    df['avg_volume_20'] = df['Volume'].rolling(20).mean()


    # ================= FINAL CLEAN =================
    df = df.dropna().reset_index(drop=True)

    # ================= SAVE =================
    df.to_csv(csv_path, index=False)

    print(f"✅ Features created successfully | Rows: {len(df)}")
    print(
        "Added: SMA20, SMA50, EMA50, EMA200, RSI, ATR, ADX, "
        "Volume_SMA20, Time Filters\n"
    )


# ================= RUN =================



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(BASE_DIR, "data", "csvfile")

for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        build_features(os.path.join(folder_path, filename))

       


