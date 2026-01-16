import pandas as pd
import numpy as np
import matplotlib.pyplot as plt




def define(path_run):
        # ================== LOAD DATA ==================
        df = pd.read_csv(path_run)
        df["Date"] = pd.to_datetime(df["Date"])
        df["date_only"] = df["Date"].dt.date
        df["avg_volume_20"] = df["Volume"].rolling(20).mean()


        # ================== PARAMETERS ==================
        ATR_MULT = 1.5
        TREND_THRESHOLD = 0.01
        EMA_MEET_THRESHOLD = 0.001
        SLOPE_THRESHOLD = 0.0005


        INITIAL_CAPITAL = 10000
        FIXED_CAPITAL_PER_TRADE = 10000  # 🔒 Exactly 10k worth of shares per trade, no compounding


        RSI_ENTRY_LOW = 40
        RSI_ENTRY_HIGH = 60
        RSI_LONG_TP = 70
        RSI_SHORT_TP = 30


        # ================== CLEAN ==================
        df = df.dropna().reset_index(drop=True)


        # ================== STATE ==================
        cash = INITIAL_CAPITAL
        position = 0
        direction = 0
        entry_price = 0
        shares = 0
        sl = 0


        capital_curve = np.zeros(len(df))
        capital_curve[0] = INITIAL_CAPITAL
        trade_returns = []


        buy_x, buy_y = [], []
        sell_x, sell_y = [], []
        exit_x, exit_y = [], []


        # ================== BACKTEST ==================
        for i in range(1, len(df)):


            price = df.loc[i, "Close"]
            ema50 = df.loc[i, "ema_50"]
            ema200 = df.loc[i, "ema_200"]
            ema50_prev = df.loc[i - 1, "ema_50"]
            rsi = df.loc[i, "rsi"]
            atr = df.loc[i, "atr"]
            volume = df.loc[i, "Volume"]
            avg_volume_20 = df.loc[i, "avg_volume_20"]


            trend_strength = abs(ema50 - ema200) / price
            ema50_slope = (ema50 - ema50_prev) / ema50_prev
            volume_condition = volume > avg_volume_20


            capital_curve[i] = cash


            # ================= ENTRY =================
            if position == 0 and trend_strength > TREND_THRESHOLD and volume_condition:


                if ema50 > ema200 and price > ema50 and ema50_slope > SLOPE_THRESHOLD and RSI_ENTRY_LOW <= rsi <= RSI_ENTRY_HIGH:
                    direction = 1
                elif ema50 < ema200 and price < ema50 and ema50_slope < -SLOPE_THRESHOLD and RSI_ENTRY_LOW <= rsi <= RSI_ENTRY_HIGH:
                    direction = -1
                else:
                    continue


                position = 1
                entry_price = price
                # 🔄 MODIFIED: Buy exactly 10k worth of shares (like 10 shares if stock=1000)
                shares = FIXED_CAPITAL_PER_TRADE / entry_price  # e.g., 10000/1000 = 10 shares


                if direction == 1:
                    buy_x.append(i)
                    buy_y.append(price)
                    sl = entry_price - ATR_MULT * atr
                else:
                    sell_x.append(i)
                    sell_y.append(price)
                    sl = entry_price + ATR_MULT * atr


            # ================= EXIT =================
            elif position == 1:


                exit_trade = False


                # STOP LOSS
                if direction == 1 and price <= sl:
                    exit_trade = True
                elif direction == -1 and price >= sl:
                    exit_trade = True


                # TAKE PROFIT
                if not exit_trade:
                    if direction == 1 and (rsi >= RSI_LONG_TP or abs(ema50 - ema200) / price < EMA_MEET_THRESHOLD):
                        exit_trade = True
                    elif direction == -1 and (rsi <= RSI_SHORT_TP or abs(ema50 - ema200) / price < EMA_MEET_THRESHOLD):
                        exit_trade = True


                if exit_trade:
                    pnl = (price - entry_price) * shares if direction == 1 else (entry_price - price) * shares
                    cash += pnl  # Cash gets PnL from 10k position


                    trade_returns.append(pnl / FIXED_CAPITAL_PER_TRADE)


                    exit_x.append(i)
                    exit_y.append(price)


                    position = 0
                    direction = 0
                    shares = 0


        # ================== RESULTS ==================
        df["capital"] = capital_curve


        total_return = (cash - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
        annual_return = total_return / 5


        wins = [r for r in trade_returns if r > 0]
        losses = [r for r in trade_returns if r < 0]

        print("=========result==================")
        print("Staring Capital :",INITIAL_CAPITAL)
        print("Final Capital   :", round(cash, 2))
        print("Total Return    :", round(total_return, 2))

        print("\n=====================")
        print("Trades          :", len(trade_returns))
        print("Win Rate        :", round(len(wins) / len(trade_returns) * 100, 2))
        print("Avg Win         :", round(np.mean(wins) * 100, 2) if wins else 0)
        print("Avg Loss        :", round(np.mean(losses) * 100, 2) if losses else 0)


        # ================== PLOT ==================
       
       #plt.figure(figsize=(15, 10))


        #plt.subplot(2, 1, 1)
        #plt.plot(df["Close"], label="Close")
        #plt.plot(df["ema_50"], label="EMA 50")
        #plt.plot(df["ema_200"], label="EMA 200")
        #plt.scatter(buy_x, buy_y, marker="^", color="green", s=80, label="Buy")
        #plt.scatter(sell_x, sell_y, marker="v", color="red", s=80, label="Sell")
        #plt.scatter(exit_x, exit_y, marker=">", color="purple", s=80, label="Exit")
        #plt.legend()
        #plt.title("Price + EMA + Trades")


        #plt.subplot(2, 1, 2)
        #plt.plot(df["Date"], df["capital"], color="black", linewidth=2, label="Capital Curve")
        #plt.axhline(y=INITIAL_CAPITAL, color="red", linestyle="--", label="Initial Capital")
        #plt.legend()
        #plt.title("Equity Curve (Fixed 10k Per Trade, No Compounding)")


        #plt.tight_layout()
        #plt.show()
        
print("\n adanipower")
define("data/csvfile/adanipower_2020_2025_daily.csv")

print("\n bel")
define("data/csvfile/bel_2020_2025_daily.csv")

print("\n infy")
define("data/csvfile/infy_2020_2025_daily.csv")

print("\nitc")
define("data/csvfile/itc_2020_2025_daily.csv")

print("\nsail")
define("data/csvfile/sail_2020_2025_daily.csv")

print("\n bin")
define("data/csvfile/sbin_2020_2025_daily.csv")

print("\n tatpower")
define("data/csvfile/tatapower_2020_2025_daily.csv")

print("\n wipro")
define("data/csvfile/wipro_2020_2025_daily.csv")