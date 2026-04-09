import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(layout="wide")
st.title("📊 Swiss Market Dashboard")

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

st.subheader("🟩 SLI Heatmap")

cols = st.columns(5)

for i,row in stocks.iterrows():
    cols[i % 5].metric(
        row["Ticker"],
        round(row["Preis"],2),
        row["Tag %"]
    )

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


