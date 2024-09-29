import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Real-Time Business Growth Dashboard",
    layout="wide"
)

st.title("📊 Real-Time Business Performance & Growth Dashboard")
st.caption("Cloud-safe deployed analytics dashboard")

# --------------------------------------------------
# DATA PATHS
# --------------------------------------------------
DATA_DIR = "data/processed"
CORE_FILE = os.path.join(DATA_DIR, "core_kpis.csv")
GROWTH_FILE = os.path.join(DATA_DIR, "growth_metrics.csv")
RISK_FILE = os.path.join(DATA_DIR, "risk_metrics.csv")
DEMAND_FILE = os.path.join(DATA_DIR, "demand_alignment.csv")
INSIGHTS_FILE = os.path.join(DATA_DIR, "auto_insights.txt")

# --------------------------------------------------
# BOOTSTRAP DATA (VERY IMPORTANT FOR CLOUD)
# --------------------------------------------------
def bootstrap_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(CORE_FILE):
        pd.DataFrame([{
            "total_revenue": 0,
            "avg_hourly_revenue": 0,
            "avg_price": 0,
            "total_trades": 0
        }]).to_csv(CORE_FILE, index=False)

    if not os.path.exists(GROWTH_FILE):
        pd.DataFrame(columns=["event_time", "revenue_growth_pct"]).to_csv(GROWTH_FILE, index=False)

    if not os.path.exists(RISK_FILE):
        pd.DataFrame(columns=["event_time", "price_volatility", "high_volatility_flag"]).to_csv(RISK_FILE, index=False)

    if not os.path.exists(DEMAND_FILE):
        pd.DataFrame(columns=["event_time", "revenue_trend", "demand_trend"]).to_csv(DEMAND_FILE, index=False)

    if not os.path.exists(INSIGHTS_FILE):
        with open(INSIGHTS_FILE, "w") as f:
            f.write("No insights generated yet.\n")

bootstrap_data()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
core = pd.read_csv(CORE_FILE)
growth = pd.read_csv(GROWTH_FILE)
risk = pd.read_csv(RISK_FILE)
demand = pd.read_csv(DEMAND_FILE)

for df in [growth, risk, demand]:
    if not df.empty and "event_time" in df.columns:
        df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce")

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.subheader("🔑 Executive KPIs")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Revenue", round(core["total_revenue"][0], 2))
c2.metric("Avg Hourly Revenue", round(core["avg_hourly_revenue"][0], 2))
c3.metric("Avg Price", round(core["avg_price"][0], 2))
c4.metric("Total Trades", int(core["total_trades"][0]))

# --------------------------------------------------
# REVENUE GROWTH
# --------------------------------------------------
st.subheader("📈 Revenue Growth")

if growth.shape[0] > 1:
    fig = px.line(
        growth,
        x="event_time",
        y="revenue_growth_pct",
        title="Revenue Growth (%) Over Time"
    )
    st.plotly_chart(fig, width="stretch")
else:
    st.info("Revenue growth data will appear once more data is available.")

# --------------------------------------------------
# VOLATILITY RISK
# --------------------------------------------------
st.subheader("🚨 Volatility Risk")

if risk.shape[0] > 1:
    fig = px.line(
        risk,
        x="event_time",
        y="price_volatility",
        title="Price Volatility Over Time"
    )
    st.plotly_chart(fig, width="stretch")

    if risk["high_volatility_flag"].sum() > 0:
        st.warning("⚠️ High volatility detected")
    else:
        st.success("✅ Market volatility is within safe limits")
else:
    st.info("Volatility data not available yet.")

# --------------------------------------------------
# DEMAND VS REVENUE
# --------------------------------------------------
st.subheader("🔍 Demand vs Revenue Alignment")

if demand.shape[0] > 1:
    fig = px.line(
        demand,
        x="event_time",
        y=["revenue_trend", "demand_trend"],
        title="Demand vs Revenue Trend Comparison"
    )
    st.plotly_chart(fig, width="stretch")
else:
    st.info("Demand vs revenue trends will appear once data accumulates.")

# --------------------------------------------------
# AUTO INSIGHTS
# --------------------------------------------------
st.subheader("🧠 Automated Business Insights")

with open(INSIGHTS_FILE, "r", encoding="utf-8") as f:
    st.text(f.read())

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.caption(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
