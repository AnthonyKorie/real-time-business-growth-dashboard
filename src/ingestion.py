"""
PHASE 1: REAL-TIME DATA INGESTION (OPTION A)

This module fetches:
1. Live transaction-like events from Binance (real-time trades)
2. Live demand signal from Google Trends

Both are stored as timestamped snapshots for analytics.
"""

import requests
import pandas as pd
from datetime import datetime
import os
from pytrends.request import TrendReq


# -----------------------------
# CONFIGURATION
# -----------------------------

BINANCE_TRADES_API = "https://api.binance.com/api/v3/trades"
SYMBOL = "BTCUSDT"  # Business entity (product)
RAW_DATA_DIR = "data/raw"


# -----------------------------
# BINANCE LIVE TRADES
# -----------------------------

def fetch_live_trades(limit=500):
    """
    Fetch live trades from Binance.
    Each trade is treated as a transaction event.
    """

    params = {
        "symbol": SYMBOL,
        "limit": limit
    }

    response = requests.get(BINANCE_TRADES_API, params=params)
    response.raise_for_status()

    trades = response.json()

    df = pd.DataFrame(trades)

    # Convert timestamp
    df["event_time"] = pd.to_datetime(df["time"], unit="ms")

    # Business-style columns
    df["price"] = df["price"].astype(float)
    df["quantity"] = df["qty"].astype(float)
    df["revenue"] = df["price"] * df["quantity"]

    df["product"] = SYMBOL
    df["buyer_maker"] = df["isBuyerMaker"]

    return df[
        ["event_time", "product", "price", "quantity", "revenue", "buyer_maker"]
    ]


# -----------------------------
# GOOGLE TRENDS DEMAND SIGNAL
# -----------------------------

def fetch_google_trends(keyword="Bitcoin"):
    """
    Fetch real-time demand signal from Google Trends.
    """

    pytrends = TrendReq(hl="en-US", tz=330)

    pytrends.build_payload(
        kw_list=[keyword],
        timeframe="now 7-d"
    )

    trends = pytrends.interest_over_time().reset_index()

    if "isPartial" in trends.columns:
        trends = trends.drop(columns=["isPartial"])

    trends.rename(columns={keyword: "search_interest"}, inplace=True)

    return trends


# -----------------------------
# SAVE SNAPSHOTS
# -----------------------------

def save_snapshot(df, prefix):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{RAW_DATA_DIR}/{prefix}_{timestamp}.csv"

    df.to_csv(path, index=False)
    return path


# -----------------------------
# MAIN EXECUTION
# -----------------------------

if __name__ == "__main__":

    trades_df = fetch_live_trades()
    trades_file = save_snapshot(trades_df, "binance_trades")

    trends_df = fetch_google_trends()
    trends_file = save_snapshot(trends_df, "google_trends")

    print("✅ Real-time ingestion completed")
    print(f"Trades rows: {trades_df.shape[0]}")
    print(f"Trades snapshot: {trades_file}")
    print(f"Trends snapshot: {trends_file}")
