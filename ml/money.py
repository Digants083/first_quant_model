# ml_prob_backtest_with_stats.py
# End-to-end: trade using ML probabilities + backtest + t-test + bootstrap confidence

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_1samp

# ================== PATH ==================
PATH = "csvfile/tatapower_2020_2025_daily_ml_probs.csv"  # change per stock

# ================== LOAD ==================
df = pd.read_csv(PATH)
df["Date"] = pd.to_datetime(df["Date"])

# ================== PARAMETERS ==================
INITIAL_CAPITAL = 10000
RISK_PER_TRADE = 0.02        # 2% risk per trade
SL_PCT = 0.02                # 2% stop loss
TP_PCT = 0.04                # 4% take profit
LONG_PROB = 0.60
SHORT_PROB = 0.40

# ================== STATE ==================
cash = INITIAL_CAPITAL
position = 0        # 1 long, -1 short, 0 flat
entry = 0
shares = 0

equity = [INITIAL_CAPITAL]
trade_returns = []
trade_log = []

# ================== BACKTEST ==================
for i in range(1, len(df)):
    price = df.loc[i, "Close"]
    prob = df.loc[i, "prob_up"]

    equity.append(cash + shares * price)

    # ENTRY
    if position == 0:
        risk_amt = cash * RISK_PER_TRADE
        if prob > LONG_PROB:
            position = 1
            entry = price
            shares = risk_amt / (price * SL_PCT)
        elif prob < SHORT_PROB:
            position = -1
            entry = price
            shares = risk_amt / (price * SL_PCT)

    # EXIT
    elif position != 0:
        if position == 1:
            if price <= entry*(1-SL_PCT) or price >= entry*(1+TP_PCT):
                pnl = (price-entry)*shares
                cash += pnl
                trade_returns.append(pnl / INITIAL_CAPITAL)
                trade_log.append((df.loc[i, "Date"], position, entry, price, pnl))
                position = 0
                shares = 0
        else:
            if price >= entry*(1+SL_PCT) or price <= entry*(1-TP_PCT):
                pnl = (entry-price)*shares
                cash += pnl
                trade_returns.append(pnl / INITIAL_CAPITAL)
                trade_log.append((df.loc[i, "Date"], position, entry, price, pnl))
                position = 0
                shares = 0

# ================== RESULTS ==================
final_capital = equity[-1]
total_return = (final_capital/INITIAL_CAPITAL - 1) * 100
years = (df["Date"].iloc[-1] - df["Date"].iloc[0]).days / 365.25
cagr = ((final_capital/INITIAL_CAPITAL)**(1/years) - 1) * 100

wins = [r for r in trade_returns if r > 0]
losses = [r for r in trade_returns if r < 0]

print("\n===== ML PROBABILITY BACKTEST RESULTS =====")
print("Final Capital :", round(final_capital, 2))
print("Total Return  :", round(total_return, 2), "%")
print("CAGR          :", round(cagr, 2), "%")
print("Trades        :", len(trade_returns))
print("Win Rate      :", round(len(wins)/len(trade_returns)*100, 2) if trade_returns else 0)
print("Avg Win       :", round(np.mean(wins)*100, 2) if wins else 0)
print("Avg Loss      :", round(np.mean(losses)*100, 2) if losses else 0)

# ================== T-TEST ==================
r = np.array(trade_returns)
t_stat, p_val = ttest_1samp(r, 0)

print("\n===== T-TEST =====")
print("Mean Return per Trade :", round(np.mean(r)*100, 4), "%")
print("T-Statistic           :", round(t_stat, 4))
print("P-Value               :", round(p_val, 6))
print("EDGE:", "REAL" if p_val < 0.05 else "NO EDGE")

# ================== BOOTSTRAP CONFIDENCE ==================
boot_means = []
for _ in range(10000):
    sample = np.random.choice(r, size=len(r), replace=True)
    boot_means.append(np.mean(sample))

ci_low, ci_high = np.percentile(boot_means, [2.5, 97.5])

print("\n===== BOOTSTRAP CONFIDENCE =====")
print("95% CI:", round(ci_low*100, 3), "% to", round(ci_high*100, 3), "%")
print("PROFIT PROBABILITY:", "HIGH" if ci_low > 0 else "LOW")

# ================== PLOT ==================
plt.figure(figsize=(12,6))
plt.plot(equity, label="Equity Curve")
plt.title("ML Probability Trading Equity Curve")
plt.xlabel("Time")
plt.ylabel("Capital")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
