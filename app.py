
import streamlit as st
import pandas as pd
from pathlib import Path

from src.data_fetcher import fetch_stock_data
from src.models.scoring import add_scores
from src.utils.helpers import money, pct

st.set_page_config(page_title="Luc Investment Terminal V3", page_icon="📈", layout="wide")

st.title("📈 Luc Investment Terminal V3")
st.caption("Version 3.0 Foundation — stable portfolio dashboard with live data, scoring, valuation, debt, risk, and alerts.")

PORTFOLIO_PATH = Path("src/data/portfolio.csv")

if not PORTFOLIO_PATH.exists():
    st.error("Missing file: src/data/portfolio.csv")
    st.stop()

portfolio = pd.read_csv(PORTFOLIO_PATH)
portfolio["Ticker"] = portfolio["Ticker"].astype(str).str.upper().str.strip()

with st.sidebar:
    st.header("Settings")
    portfolio_value = st.number_input("Portfolio value ($)", min_value=0.0, value=2500.0, step=100.0)
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()

with st.spinner("Fetching live market data..."):
    live = fetch_stock_data(portfolio["Ticker"].tolist())

df = portfolio.merge(live, on="Ticker", how="left")
df = add_scores(df)
df["Dollar Allocation"] = portfolio_value * df["Weight"] / 100
df["Net Debt"] = df["Total Debt"] - df["Cash"]

weighted_score = (df["Total Score /100"] * df["Weight"]).sum() / max(df["Weight"].sum(), 1)
ai_exposure = ((df["AI Exposure /10"] / 10) * df["Weight"]).sum()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Portfolio Value", f"${portfolio_value:,.0f}")
c2.metric("Holdings", len(df))
c3.metric("Total Weight", f"{df['Weight'].sum():.1f}%")
c4.metric("Weighted Score", f"{weighted_score:.1f}/100")
c5.metric("AI Exposure", f"{ai_exposure:.1f}%")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Portfolio",
    "Scorecard",
    "Debt & Valuation",
    "Market Risk",
    "Alerts"
])

with tab1:
    st.subheader("Portfolio Overview")
    view = df[[
        "Ticker", "Company", "Weight", "Dollar Allocation", "Price",
        "Revenue Growth", "Forward P/E", "PEG", "Total Score /100", "Rating"
    ]]
    st.dataframe(view, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("100-Point Company Scorecard")
    score_view = df[[
        "Ticker", "Company", "Revenue Score /20", "Earnings Score /20",
        "FCF Score /15", "Valuation Score /15", "Debt Score /10",
        "Moat /10", "Management /5", "Market Opportunity /5",
        "AI Exposure /10", "Total Score /100", "Rating"
    ]].sort_values("Total Score /100", ascending=False)
    st.dataframe(score_view, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Debt & Valuation Monitor")
    debt_view = df[[
        "Ticker", "Company", "Market Cap", "Forward P/E", "Trailing P/E",
        "PEG", "Price/Sales", "Total Debt", "Cash", "Net Debt",
        "Debt Score /10", "Valuation Score /15"
    ]]
    st.dataframe(debt_view, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Market Crisis Dashboard")
    crisis = pd.DataFrame([
        ["Market Valuations", 20, 13, "AI/growth valuations are elevated"],
        ["Interest Rates", 15, 9, "Watch Fed policy and bond yields"],
        ["Credit Markets", 15, 13, "No major stress signal"],
        ["Corporate Earnings", 15, 14, "Mega-cap earnings remain strong"],
        ["Unemployment", 10, 8, "Labor market remains important"],
        ["Consumer Spending", 10, 7, "Watch slowdown signs"],
        ["Yield Curve", 10, 6, "Monitor inversion or re-steepening"],
        ["Speculation", 5, 3, "AI optimism is elevated"],
    ], columns=["Indicator", "Max Points", "Current Score", "Comment"])
    total = crisis["Current Score"].sum()
    r1, r2 = st.columns(2)
    r1.metric("Market Health Score", f"{total}/100")
    r2.metric("Estimated Crisis Risk", f"{100-total}%")
    st.dataframe(crisis, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("Smart Alerts")
    alerts = []
    for _, r in df.iterrows():
        if r["Valuation Score /15"] <= 5:
            alerts.append([r["Ticker"], "Valuation", "🔴 Expensive valuation"])
        if r["Debt Score /10"] <= 3:
            alerts.append([r["Ticker"], "Debt", "🔴 Heavy debt risk"])
        if pd.notna(r.get("Free Cash Flow")) and r["Free Cash Flow"] < 0:
            alerts.append([r["Ticker"], "Cash Flow", "🟡 Negative free cash flow"])
        if r["Total Score /100"] < 70:
            alerts.append([r["Ticker"], "Quality", "🟠 Speculative / watch closely"])

    if alerts:
        st.dataframe(pd.DataFrame(alerts, columns=["Ticker", "Type", "Alert"]), use_container_width=True, hide_index=True)
    else:
        st.success("No major alerts under the current rules.")

st.caption("Educational tool only. Verify important numbers with official company filings.")
