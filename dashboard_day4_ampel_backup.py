import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(layout="wide")
st.title("📊 Swiss Market Dashboard")

st.subheader("📊 Markt-Ampel")

markets = {
    "S&P 500": "^GSPC",
    "Euro Stoxx 50": "^STOXX50E",
    "SMI": "^SSMI"
}

changes = []

for ticker in markets.values():
    data = yf.Ticker(ticker).history(period="2d")

    if len(data) >= 2:
        change = ((data["Close"].iloc[-1] / data["Close"].iloc[-2]) - 1) * 100
        changes.append(change)

avg_change = sum(changes) / len(changes)

if avg_change > 0.3:
    st.success("🟢 Markt positiv")
elif avg_change < -0.3:
    st.error("🔴 Markt negativ")
else:
    st.warning("🟡 Markt neutral")

st.subheader("🌍 Global Market Radar")

markets = {
    "S&P 500": "^GSPC",
    "Euro Stoxx 50": "^STOXX50E",
    "SMI": "^SSMI",
    "Bitcoin": "BTC-USD",
    "Gold": "GC=F",
    "Oil": "CL=F"
}

radar_data = []

for name, ticker in markets.items():
    data = yf.Ticker(ticker).history(period="2d")

    if len(data) >= 2:
        change = ((data["Close"].iloc[-1] / data["Close"].iloc[-2]) - 1) * 100
    else:
        change = 0

    radar_data.append({
        "Market": name,
        "Change %": change
    })

radar = pd.DataFrame(radar_data)

fig = px.bar(
    radar,
    x="Market",
    y="Change %",
    color="Change %",
    color_continuous_scale=["red","white","green"],
    title="Global Market Performance"
)

st.plotly_chart(fig)

# Daten laden
stocks = pd.read_csv("stocks.csv")
crypto = pd.read_csv("crypto.csv")
commodities = pd.read_csv("commodities.csv")
indices = pd.read_csv("indices.csv")

# Kopie für Sortierungen
stocks_num = stocks.copy()

# Trendfunktion
def trend(v):
    try:
        v = float(v)
    except:
        return "⚪ 0.00%"

    if v > 0:
        return f"🟢 ▲ {v:.2f}%"
    elif v < 0:
        return f"🔴 ▼ {v:.2f}%"
    else:
        return f"⚪ {v:.2f}%"

# Farben anwenden
stocks["Tag %"] = stocks["Tag %"].apply(trend)
stocks["Monat %"] = stocks["Monat %"].apply(trend)

crypto["Tag %"] = crypto["Tag %"].apply(trend)
crypto["Monat %"] = crypto["Monat %"].apply(trend)

commodities["Tag %"] = commodities["Tag %"].apply(trend)
commodities["Monat %"] = commodities["Monat %"].apply(trend)

indices["Tag %"] = indices["Tag %"].apply(trend)
indices["Monat %"] = indices["Monat %"].apply(trend)

st.subheader("🧠 SMI Marktstimmung")

up = stocks["Tag %"].astype(str).str.contains("🟢").sum()
down = stocks["Tag %"].astype(str).str.contains("🔴").sum()
flat = stocks["Tag %"].astype(str).str.contains("⚪").sum()

c1,c2,c3 = st.columns(3)

c1.metric("🟢 Steigend", up)
c2.metric("🔴 Fallend", down)
c3.metric("⚪ Unverändert", flat)

st.subheader("🟩 SMI Heatmap")

cols = st.columns(5)

for i,row in stocks.iterrows():
    cols[i % 5].metric(
        row["Ticker"],
        round(row["Preis"],2),
        row["Tag %"]
    )

st.subheader("SMI Heatmap PRO")

heatmap2 = pd.read_csv("stocks.csv")

heatmap2["Tag %"] = pd.to_numeric(heatmap2["Tag %"], errors="coerce")

fig = px.treemap(
    heatmap2,
    path=["Ticker"],
    values="Tag %",
    color="Tag %",
    color_continuous_scale=["red","white","green"]
)

st.plotly_chart(fig)

st.subheader("🚀 Top Movers des Tages")

stocks_movers = pd.read_csv("stocks.csv")
stocks_movers["Tag %"] = pd.to_numeric(stocks_movers["Tag %"], errors="coerce")

top_up = stocks_movers.sort_values("Tag %", ascending=False).head(3)
top_down = stocks_movers.sort_values("Tag %").head(3)

col1, col2 = st.columns(2)

with col1:
    st.write("🟢 Gewinner")
    st.dataframe(top_up[["Ticker","Tag %"]])

with col2:
    st.write("🔴 Verlierer")
    st.dataframe(top_down[["Ticker","Tag %"]])

# Gewinner / Verlierer
st.subheader("🚀 SLI Gewinner")
st.dataframe(stocks.sort_values("Tag %", ascending=False).head(10))

st.subheader("📉 SLI Verlierer")
st.dataframe(stocks.sort_values("Tag %").head(10))

# Dividenden Champions
st.subheader("🏆 Dividenden Champions")
st.dataframe(stocks.sort_values("Dividende %", ascending=False).head(5))

# Kryptos
st.subheader("🪙 Kryptos")
st.dataframe(crypto)

# Rohstoffe
st.subheader("⛏ Rohstoffe")
st.dataframe(commodities)

# Indizes
st.subheader("🌍 Indizes")
st.dataframe(indices)

# Trenddiagramm
st.subheader("📈 Aktien Trend")

ticker = st.selectbox("SLI Aktie wählen", stocks["Ticker"])
data = yf.Ticker(ticker + ".SW").history(period="1y")

fig = px.line(data, y="Close", title=ticker)
st.plotly_chart(fig)

