# ml_alpha_model.py
# Train a probabilistic alpha model to predict if next 5-day return is positive
# Uses engineered features + Logistic Regression (baseline)

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ================== LOAD DATA ==================
PATH = "csvfile/tatapower_2020_2025_daily.csv"   # change per stock or loop over many

df = pd.read_csv(PATH)
df["Date"] = pd.to_datetime(df["Date"])


# ================== TARGET ==================
# 1 if next 5-day return is positive, else 0
H = 5
df["future_ret_5"] = df["Close"].shift(-H) / df["Close"] - 1
df["y"] = (df["future_ret_5"] > 0).astype(int)

# ================== FINAL DATASET ==================
features = [
    "dist_ema50", "rsi_slope", "volatility", "vol_contraction", "breakout",
    "ema_50", "ema_200", "rsi"
]

df = df.dropna().reset_index(drop=True)
X = df[features]
y = df["y"]

# ================== TRAIN / TEST SPLIT (TIME-SERIES SAFE) ==================
# 2020-2023 train, 2024-2025 test
split_date = pd.Timestamp("2024-01-01")
train_idx = df["Date"] < split_date
test_idx = df["Date"] >= split_date

X_train, y_train = X[train_idx], y[train_idx]
X_test, y_test = X[test_idx], y[test_idx]

# ================== MODEL ==================
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=2000))
])

pipe.fit(X_train, y_train)

# ================== EVALUATION ==================
proba = pipe.predict_proba(X_test)[:, 1]
pred = (proba > 0.6).astype(int)  # trade only when probability > 0.6

auc = roc_auc_score(y_test, proba)
print("AUC:", round(auc, 4))
print(classification_report(y_test, pred))

# ================== SAVE PROBABILITIES FOR TRADING ==================
out = df.loc[test_idx, ["Date", "Close"]].copy()
out["prob_up"] = proba
out.to_csv(PATH.replace(".csv", "_ml_probs.csv"), index=False)
print("Saved probabilities to:", PATH.replace(".csv", "_ml_probs.csv"))

