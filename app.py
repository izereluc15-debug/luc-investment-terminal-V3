
import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_stock_data(tickers):
    rows = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            rows.append({
                "Ticker": ticker,
                "Live Company": info.get("shortName", ticker),
                "Price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "Market Cap": info.get("marketCap"),
                "Forward P/E": info.get("forwardPE"),
                "Trailing P/E": info.get("trailingPE"),
                "PEG": info.get("pegRatio"),
                "Price/Sales": info.get("priceToSalesTrailing12Months"),
                "Revenue Growth": info.get("revenueGrowth"),
                "Earnings Growth": info.get("earningsGrowth"),
                "Profit Margin": info.get("profitMargins"),
                "Free Cash Flow": info.get("freeCashflow"),
                "Total Debt": info.get("totalDebt"),
                "Cash": info.get("totalCash"),
                "Debt/Equity": info.get("debtToEquity"),
                "Sector": info.get("sector"),
                "Industry": info.get("industry"),
            })
        except Exception as e:
            rows.append({
                "Ticker": ticker,
                "Live Company": ticker,
                "Error": str(e)
            })
    return pd.DataFrame(rows)
