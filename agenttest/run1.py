import pandas as pd
import numpy as np

def define(path_run):

    df = pd.read_csv(path_run)
    df["Date"] = pd.to_datetime(df["Date"])
    df["date_only"] = df["Date"].dt.date

  

    df = df.dropna().reset_index(drop=True)

    INITIAL_CAPITAL = 10000
    FIXED_CAPITAL_PER_TRADE = 10000
    cash = INITIAL_CAPITAL
    position = 0
    direction = 0
    entry_price = 0
    shares = 0
    sl = 0

    trade_returns = []

    for i in range(1, len(df)):

        price = df.loc[i,"Close"]
        ema50 = df.loc[i,"ema_50"]
        ema200 = df.loc[i,"ema_200"]
        rsi = df.loc[i,"rsi"]
        atr = df.loc[i,"atr"]

        dist = df.loc[i,"dist_ema50"]
        rsi_slope = df.loc[i,"rsi_slope"]
        vol_contr = df.loc[i,"vol_contraction"]
        breakout = df.loc[i,"breakout"]

        # ===== ENTRY (ALPHA SIGNAL) =====
        if position == 0:

            if (
                ema50 > ema200 and
                dist > 0.01 and
                rsi_slope > 3 and
                vol_contr and
                breakout
            ):
                direction = 1

            elif (
                ema50 < ema200 and
                dist < -0.01 and
                rsi_slope < -3 and
                vol_contr and
                breakout
            ):
                direction = -1
            else:
                continue

            position = 1
            entry_price = price
            shares = FIXED_CAPITAL_PER_TRADE / price

            sl = entry_price - 1.5 * atr if direction == 1 else entry_price + 1.5 * atr
            tp = entry_price + 3 * atr if direction == 1 else entry_price - 3 * atr

        # ===== EXIT =====
        elif position == 1:

            exit_trade = False

            if direction == 1 and (price <= sl or price >= tp):
                exit_trade = True
            elif direction == -1 and (price >= sl or price <= tp):
                exit_trade = True

            if exit_trade:
                pnl = (price - entry_price) * shares if direction == 1 else (entry_price - price) * shares
                cash += pnl
                trade_returns.append(pnl / FIXED_CAPITAL_PER_TRADE)

                position = 0
                direction = 0
                shares = 0

    # ===== RESULTS =====
    wins = [r for r in trade_returns if r > 0]
    losses = [r for r in trade_returns if r < 0]

    print("\n", path_run)
    print("Trades:", len(trade_returns))
    print("Win Rate:", round(len(wins)/len(trade_returns)*100,2) if trade_returns else 0)
    print("Mean Return:", round(np.mean(trade_returns)*100,2) if trade_returns else 0)
print("\n adanipower")
define("csvfile/adanipower_2020_2025_daily.csv")

print("\n bel")
define("csvfile/bel_2020_2025_daily.csv")

print("\n infy")
define("csvfile/infy_2020_2025_daily.csv")

print("\nitc")
define("csvfile/itc_2020_2025_daily.csv")

print("\nsail")
define("csvfile/sail_2020_2025_daily.csv")

print("\n bin")
define("csvfile/sbin_2020_2025_daily.csv")

print("\n tatpower")
define("csvfile/tatapower_2020_2025_daily.csv")

print("\n wipro")
define("csvfile/wipro_2020_2025_daily.csv")