"""
PHASE 3: BUSINESS METRICS ENGINE

This module computes:
- Core performance KPIs
- Growth & momentum metrics
- Risk indicators
- Demand vs revenue alignment metrics
"""

import pandas as pd
import numpy as np
import os


# -----------------------------
# CONFIGURATION
# -----------------------------

PROCESSED_DATA_DIR = "data/processed"
OUTPUT_DIR = "data/processed"


# -----------------------------
# LOAD DATA
# -----------------------------

def load_data():
    trades_metrics = pd.read_csv(
        f"{PROCESSED_DATA_DIR}/trades_metrics.csv",
        parse_dates=["event_time"]
    )

    business_data = pd.read_csv(
        f"{PROCESSED_DATA_DIR}/business_metrics_with_demand.csv",
        parse_dates=["event_time"]
    )

    return trades_metrics, business_data


# -----------------------------
# CORE BUSINESS KPIs
# -----------------------------

def compute_core_kpis(df):
    """
    Executive-level KPIs.
    """

    kpis = {
        "total_revenue": df["total_revenue"].sum(),
        "avg_hourly_revenue": df["total_revenue"].mean(),
        "max_hourly_revenue": df["total_revenue"].max(),
        "avg_price": df["avg_price"].mean(),
        "total_volume": df["trade_volume"].sum(),
        "total_trades": df["trade_count"].sum()
    }

    return pd.DataFrame([kpis])


# -----------------------------
# GROWTH METRICS
# -----------------------------

def compute_growth_metrics(df):
    """
    Growth & momentum indicators.
    """

    growth = df[[
        "event_time",
        "revenue_growth_pct",
        "volume_growth_pct"
    ]].copy()

    growth["revenue_growth_pct_ma"] = (
        growth["revenue_growth_pct"].rolling(3).mean()
    )

    return growth


# -----------------------------
# RISK METRICS
# -----------------------------

def compute_risk_metrics(df):
    """
    Risk & volatility indicators.
    """

    risk = df[[
        "event_time",
        "price_volatility",
        "order_imbalance"
    ]].copy()

    risk["high_volatility_flag"] = (
        risk["price_volatility"] >
        risk["price_volatility"].quantile(0.75)
    )

    return risk


# -----------------------------
# DEMAND ALIGNMENT METRICS
# -----------------------------

def compute_demand_alignment(df):
    """
    Compare revenue movement with demand signals.
    """

    alignment = df[[
        "event_time",
        "total_revenue",
        "search_interest"
    ]].copy()

    alignment["revenue_trend"] = (
        alignment["total_revenue"].pct_change()
    )

    alignment["demand_trend"] = (
        alignment["search_interest"].pct_change()
    )

    alignment["demand_revenue_gap"] = (
        alignment["demand_trend"] - alignment["revenue_trend"]
    )

    return alignment


# -----------------------------
# SAVE OUTPUTS
# -----------------------------

def save_outputs(**datasets):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for name, df in datasets.items():
        df.to_csv(f"{OUTPUT_DIR}/{name}.csv", index=False)


# -----------------------------
# MAIN EXECUTION
# -----------------------------

if __name__ == "__main__":

    trades_df, business_df = load_data()

    core_kpis = compute_core_kpis(trades_df)
    growth_metrics = compute_growth_metrics(trades_df)
    risk_metrics = compute_risk_metrics(trades_df)
    demand_alignment = compute_demand_alignment(business_df)

    save_outputs(
        core_kpis=core_kpis,
        growth_metrics=growth_metrics,
        risk_metrics=risk_metrics,
        demand_alignment=demand_alignment
    )

    print("✅ Phase 3 metrics engine completed")
