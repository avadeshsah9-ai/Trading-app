import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURATION ---
st.set_page_config(page_title="Avadesh's Trading Corner", layout="wide")

# --- DATA ENGINE ---
@st.cache_data(ttl=600)
def get_data(symbol, period, interval):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    return df, ticker.info, ticker.news

# --- SIDEBAR ---
st.sidebar.title("🦅 Trading Terminal")
recommendations = ["RELIANCE.NS", "TATASTEEL.NS", "INFY.NS", "HDFCBANK.NS", "NVDA", "AAPL", "BTC-USD", "TATAMOTORS.NS"]
ticker_input = st.sidebar.selectbox("Search or Select Stock", options=recommendations, index=0)
period = st.sidebar.selectbox("Period", ["1d", "5d", "1mo", "6mo", "1y", "max"])
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "1h", "1d", "1wk"])

df, info, news = get_data(ticker_input, period, interval)
full_name = info.get('longName', 'N/A')

# --- MAIN APP ---
st.title("🦅 Avadesh's Trading Corner")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard", "🔮 Prediction", "📰 News", "👀 Watchlist", "💼 Portfolio", "💰 Investments"
])

# --- DASHBOARD TAB ---
with tab1:
    st.subheader(f"{full_name} ({ticker_input})")
    if not df.empty:
        last = df.iloc[-1]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Open", f"{last['Open']:.2f}")
        c2.metric("High", f"{last['High']:.2f}")
        c3.metric("Low", f"{last['Low']:.2f}")
        c4.metric("Close", f"{last['Close']:.2f}")
        c5.metric("Volume", f"{int(last['Volume']):,}")

        # Static Chart (Zoom only, no pan)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, dragmode=False)
        # Disable panning by fixing ranges
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'pan': False})
    else:
        st.error("Data unavailable.")

# --- PREDICTION TAB ---
with tab2:
    st.header(f"🔮 Advanced Forecast: {ticker_input}")
    if not df.empty:
        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()
        df['StdDev'] = df['Close'].rolling(20).std()
        
        last_close = df['Close'].iloc[-1]
        sma20 = df['SMA20'].iloc[-1]
        sma50 = df['SMA50'].iloc[-1]
        volatility = df['StdDev'].iloc[-1]
        
        spread_pct = ((sma20 - sma50) / sma50) * 100
        direction = "Bullish" if sma20 > sma50 else "Bearish"
        target_price = last_close * (1 + (spread_pct / 100))
        rupee_diff = target_price - last_close
        
        st.write(f"### Trend Assessment: **{direction}**")
        st.write(f"The stock is currently trading {'above' if direction == 'Bullish' else 'below'} the 50-day average.")
        st.metric("Projected Price Change", f"₹{rupee_diff:.2f}", f"{spread_pct:.2f}%")
        
        st.write("---")
        st.write("### Behavior Information")
        st.write(f"• **Current Volatility:** {volatility:.2f} points (1-std deviation).")
        st.write(f"• **Target Price Calculation:** Based on a {spread_pct:.2f}% technical gap.")
        st.write("• **Note:** This forecast is a mathematical projection based on historical trends and does not constitute financial advice.")
        st.progress(min(abs(spread_pct) / 5, 1.0))
    else:
        st.write("Insufficient data for full forecast.")

# --- NEWS TAB ---
with tab3:
    st.header(f"📰 Live News Feed: {ticker_input}")
    if news:
        for item in news[:5]:
            st.markdown(f"**{item.get('title', 'Headline Unavailable')}**")
            st.write(f"Source: {item.get('publisher', 'Unknown')}")
            st.write(f"[Read Full Article]({item.get('link', '#')})")
            st.divider()
    else:
        st.info("No recent news found.")

# --- WATCHLIST ---
with tab4:
    st.header("👀 Watchlist")
    for stock in recommendations:
        d, _, _ = get_data(stock, "1d", "1d")
        if not d.empty:
            st.metric(label=stock, value=f"₹{d['Close'].iloc[-1]:.2f}")