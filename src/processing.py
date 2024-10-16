"""
PHASE 2: DATA CLEANING & FEATURE ENGINEERING (FIXED)
"""

import pandas as pd
import os
from glob import glob

# -----------------------------
# CONFIGURATION
# -----------------------------

RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"

# 🔥 FIX: finer aggregation
TIME_BUCKET = "1Min"


# -----------------------------
# LOAD LATEST SNAPSHOT
# -----------------------------

def load_latest_file(prefix):
    files = glob(f"{RAW_DATA_DIR}/{prefix}_*.csv")
    if not files:
        raise FileNotFoundError(f"No files found for prefix: {prefix}")
    return max(files, key=os.path.getctime)


# -----------------------------
# CLEAN TRADES
# -----------------------------

def clean_trades(df):
    df["event_time"] = pd.to_datetime(df["event_time"])
    df = df[(df["price"] > 0) & (df["quantity"] > 0)]
    df = df.dropna()
    return df


# -----------------------------
# AGGREGATE TRADES
# -----------------------------

def aggregate_trades(df):
    df = df.copy()
    df.set_index("event_time", inplace=True)

    agg = df.resample(TIME_BUCKET).agg(
        total_revenue=("revenue", "sum"),
        trade_volume=("quantity", "sum"),
        avg_price=("price", "mean"),
        trade_count=("revenue", "count"),
        buy_pressure=("buyer_maker", lambda x: (~x).sum()),
        sell_pressure=("buyer_maker", lambda x: x.sum())
    ).reset_index()

    return agg


# -----------------------------
# FEATURE ENGINEERING
# -----------------------------

def engineer_features(df):
    df = df.sort_values("event_time")

    df["revenue_growth_pct"] = df["total_revenue"].pct_change() * 100
    df["volume_growth_pct"] = df["trade_volume"].pct_change() * 100
    df["price_volatility"] = df["avg_price"].rolling(5).std()
    df["order_imbalance"] = df["buy_pressure"] - df["sell_pressure"]

    return df


# -----------------------------
# PROCESS GOOGLE TRENDS
# -----------------------------

def process_trends(df):
    df["event_time"] = pd.to_datetime(df["date"])
    df = df.drop(columns=["date"])
    df = df.sort_values("event_time")
    return df


# -----------------------------
# MERGE DATASETS
# -----------------------------

def merge_trades_and_trends(trades_df, trends_df):
    return pd.merge_asof(
        trades_df.sort_values("event_time"),
        trends_df.sort_values("event_time"),
        on="event_time",
        direction="backward"
    )


# -----------------------------
# SAVE PROCESSED
# -----------------------------

def save_processed(df, filename):
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    path = f"{PROCESSED_DATA_DIR}/{filename}"

    if os.path.exists(path):
        existing = pd.read_csv(path, parse_dates=["event_time"])
        df = pd.concat([existing, df]).drop_duplicates("event_time")
        df = df.sort_values("event_time")

    df.to_csv(path, index=False)



# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    trades_file = load_latest_file("binance_trades")
    trends_file = load_latest_file("google_trends")

    trades_raw = pd.read_csv(trades_file)
    trends_raw = pd.read_csv(trends_file)

    trades_clean = clean_trades(trades_raw)
    trades_agg = aggregate_trades(trades_clean)
    trades_features = engineer_features(trades_agg)

    trends_processed = process_trends(trends_raw)

    final_data = merge_trades_and_trends(trades_features, trends_processed)

    save_processed(trades_features, "trades_metrics.csv")
    save_processed(final_data, "business_metrics_with_demand.csv")

    print("✅ Phase 2 (FIXED) completed successfully")
