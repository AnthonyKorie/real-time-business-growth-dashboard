"""
PHASE 4: INTELLIGENCE LAYER

This module:
- Generates automated business insights
- Flags growth & risk alerts
- Produces decision-ready recommendations
"""

import pandas as pd
import os


# -----------------------------
# CONFIGURATION
# -----------------------------

DATA_DIR = "data/processed"
OUTPUT_FILE = "data/processed/auto_insights.txt"


# -----------------------------
# LOAD METRICS
# -----------------------------

def load_metrics():
    core = pd.read_csv(f"{DATA_DIR}/core_kpis.csv")
    growth = pd.read_csv(f"{DATA_DIR}/growth_metrics.csv")
    risk = pd.read_csv(f"{DATA_DIR}/risk_metrics.csv")
    demand = pd.read_csv(f"{DATA_DIR}/demand_alignment.csv")

    return core, growth, risk, demand


# -----------------------------
# INSIGHT GENERATORS
# -----------------------------

def generate_growth_insight(growth_df):
    recent = growth_df.tail(5)

    avg_growth = recent["revenue_growth_pct"].mean()

    if avg_growth > 2:
        return "📈 Revenue shows strong short-term growth momentum."
    elif avg_growth < -2:
        return "📉 Revenue is declining in recent periods — growth intervention needed."
    else:
        return "⚖️ Revenue growth is stable but slow — optimization opportunity exists."


def generate_risk_insight(risk_df):
    high_risk_periods = risk_df["high_volatility_flag"].sum()

    if high_risk_periods > 0:
        return "🚨 Market volatility detected — elevated business risk in recent periods."
    else:
        return "✅ Market conditions appear stable with low volatility risk."


def generate_demand_insight(demand_df):
    recent = demand_df.tail(5)

    avg_gap = recent["demand_revenue_gap"].mean()

    if avg_gap > 0:
        return "🔍 Demand is increasing faster than revenue — potential conversion or pricing gap."
    elif avg_gap < 0:
        return "💰 Revenue growth outpaces demand — momentum driven by market activity."
    else:
        return "⚖️ Demand and revenue trends are aligned."


def generate_executive_summary(core_df):
    total_revenue = core_df["total_revenue"].iloc[0]
    avg_price = core_df["avg_price"].iloc[0]

    return (
        f"📊 Executive Summary:\n"
        f"- Total Revenue Observed: {round(total_revenue, 2)}\n"
        f"- Average Transaction Price: {round(avg_price, 2)}\n"
    )


# -----------------------------
# MAIN INTELLIGENCE ENGINE
# -----------------------------

def generate_all_insights():
    core, growth, risk, demand = load_metrics()

    insights = []
    insights.append(generate_executive_summary(core))
    insights.append(generate_growth_insight(growth))
    insights.append(generate_risk_insight(risk))
    insights.append(generate_demand_insight(demand))

    return insights


# -----------------------------
# SAVE INSIGHTS
# -----------------------------

def save_insights(insights):
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for insight in insights:
            f.write(insight + "\n\n")


# -----------------------------
# MAIN EXECUTION
# -----------------------------

if __name__ == "__main__":
    insights = generate_all_insights()
    save_insights(insights)

    print("✅ Phase 4 intelligence layer completed")
    print(f"Insights saved to: {OUTPUT_FILE}")
