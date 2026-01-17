import pandas as pd
import numpy as np

ADX_THRESHOLD = 25
ATR_MULT = 1.5
TP_MULT = 2.0

def run_regime_backtest(path):

    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])

    trend_trades = []
    sideways_trades = []

    position = 0
    direction = 0
    entry = 0
    sl = 0
    tp = 0

    for i in range(1, len(df)):

        price = df.loc[i, "Close"]
        ema50 = df.loc[i, "ema_50"]
        ema200 = df.loc[i, "ema_200"]
        rsi = df.loc[i, "rsi"]
        atr = df.loc[i, "atr"]
        adx = df.loc[i, "adx"]

        # ===== ENTRY =====
        if position == 0:

            # LONG
            if ema50 > ema200 and rsi < 60 and adx > 20:
                position = 1
                direction = 1
                entry = price
                sl = entry - ATR_MULT * atr
                tp = entry + TP_MULT * atr

            # SHORT
            elif ema50 < ema200 and rsi > 40 and adx > 20:
                position = 1
                direction = -1
                entry = price
                sl = entry + ATR_MULT * atr
                tp = entry - TP_MULT * atr

        # ===== EXIT =====
        elif position == 1:

            exit_trade = False

            if direction == 1 and (price <= sl or price >= tp or rsi >= 70):
                exit_trade = True
            elif direction == -1 and (price >= sl or price <= tp or rsi <= 30):
                exit_trade = True

            if exit_trade:
                ret = (price - entry) / entry if direction == 1 else (entry - price) / entry

                if adx > ADX_THRESHOLD:
                    trend_trades.append(ret)
                else:
                    sideways_trades.append(ret)

                position = 0

    # SAVE FILES
    pd.DataFrame({"return": trend_trades}).to_csv(path.replace(".csv","_trend_trades.csv"), index=False)
    pd.DataFrame({"return": sideways_trades}).to_csv(path.replace(".csv","_sideways_trades.csv"), index=False)

    print("\nSaved regime files for:", path)


# ===== RUN =====
run_regime_backtest("csvfile/tatapower_2020_2025_daily.csv")
run_regime_backtest("csvfile/infy_2020_2025_daily.csv")
run_regime_backtest("csvfile/itc_2020_2025_daily.csv")
