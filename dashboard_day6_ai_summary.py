import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import os
from datetime import date

today = date.today()

report_path = f"/Users/adi/Library/Mobile Documents/com~apple~CloudDocs/Market Reports/Swiss_Market_Report_{today}.pdf"

if not os.path.exists(report_path):

    os.system("python3 export_pdf.py")

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

st.subheader("🌍 Globales Vorbörsen Radar")

markets = {
"S&P500": "^GSPC",
"NASDAQ": "^IXIC",
"Bitcoin": "BTC-USD",
"Gold": "GC=F",
"Oil": "CL=F"
}

for name, ticker in markets.items():

    data = yf.Ticker(ticker).history(period="2d")

    if len(data) >= 2:

        change = ((data["Close"][-1] / data["Close"][-2]) - 1) * 100

        st.write(f"{name} {trend(change)}")

st.subheader("📊 Markt-Sensitivität der SMI Aktien")

smi = yf.Ticker("^SSMI").history(period="6mo")["Close"].pct_change()

results = []

for ticker in stocks["Ticker"]:

    try:
        data = yf.Ticker(ticker + ".SW").history(period="6mo")["Close"].pct_change()

        combined = pd.concat([smi, data], axis=1).dropna()

        if len(combined) > 20:

            beta = combined.iloc[:,1].cov(combined.iloc[:,0]) / combined.iloc[:,0].var()

            results.append((ticker, beta))

    except:
        pass

beta_df = pd.DataFrame(results, columns=["Ticker","Beta"]).sort_values("Beta", ascending=False)

for i,row in beta_df.iterrows():

    b = row["Beta"]

    if b > 1.2:
        label = "🔥 stark zyklisch"
    elif b > 0.8:
        label = "⚡ moderat"
    else:
        label = "🛡 defensiv"

    st.write(f"{row['Ticker']}  {label} (Beta {b:.2f})")

st.subheader("🚨 Bull Market Scanner")

sp500 = yf.Ticker("^GSPC").history(period="2d")
nasdaq = yf.Ticker("^IXIC").history(period="2d")
btc = yf.Ticker("BTC-USD").history(period="2d")

sp_change = ((sp500["Close"][-1] / sp500["Close"][-2]) - 1) * 100
nas_change = ((nasdaq["Close"][-1] / nasdaq["Close"][-2]) - 1) * 100
btc_change = ((btc["Close"][-1] / btc["Close"][-2]) - 1) * 100

risk_on = 0

if sp_change > 0:
    risk_on += 1

if nas_change > 0:
    risk_on += 1

if btc_change > 0:
    risk_on += 1

if risk_on >= 2:

    st.write("🟢 Bullisches globales Umfeld erkannt")

    candidates = beta_df.sort_values("Beta", ascending=False).head(5)

    st.write("Interessante zyklische Aktien:")

    for i,row in candidates.iterrows():
        st.write(row["Ticker"], f"(Beta {row['Beta']:.2f})")

else:

    st.write("🔴 Kein klares Bull-Market Signal")

st.subheader("📉 SMI Volatilitäts Radar")

smi_data = yf.Ticker("^SSMI").history(period="1mo")

returns = smi_data["Close"].pct_change()

volatility = returns.std() * 100

st.write(f"Aktuelle Marktvolatilität: {volatility:.2f} %")

if volatility > 1.5:
    st.write("⚠️ erhöhte Marktbewegung erkannt")
elif volatility > 1:
    st.write("🟡 moderat bewegter Markt")
else:
    st.write("🟢 ruhiger Markt")

st.subheader("🧠 SMI Marktstimmung")

up = stocks["Tag %"].astype(str).str.contains("🟢").sum()
down = stocks["Tag %"].astype(str).str.contains("🔴").sum()
flat = stocks["Tag %"].astype(str).str.contains("⚪").sum()

c1,c2,c3 = st.columns(3)

c1.metric("🟢 Steigend", up)
c2.metric("🔴 Fallend", down)
c3.metric("⚪ Unverändert", flat)

st.subheader("🧠 Markt-Interpretation")

tag_values = pd.to_numeric(stocks["Tag %"], errors="coerce")

up = (tag_values > 0).sum()
down = (tag_values < 0).sum()

if up > down:
    st.write("Der SMI zeigt heute eine **positive Marktbreite**. Mehr Aktien steigen als fallen.")
elif down > up:
    st.write("Der SMI zeigt heute eine **schwache Marktbreite**. Mehr Aktien fallen als steigen.")
else:
    st.write("Der SMI zeigt heute eine **ausgeglichene Marktstimmung**.")

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

st.subheader("🌊 SMI Kapitalfluss Radar")

tag_values = pd.to_numeric(stocks["Tag %"], errors="coerce")

stocks["Tag_raw"] = tag_values

inflow = stocks.sort_values("Tag_raw", ascending=False).head(3)
outflow = stocks.sort_values("Tag_raw").head(3)

st.write("📈 Kapital fliesst in:")

for i, row in inflow.iterrows():
    st.write(f"{row['Ticker']} {row['Tag %']}")

st.write("📉 Kapital verlässt:")

for i, row in outflow.iterrows():
    st.write(f"{row['Ticker']} {row['Tag %']}")

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

st.subheader("🧠 Automatische Markt-Zusammenfassung")

summary = []

if sp_change > 0 and nas_change > 0:
    summary.append("Globale Aktienmärkte zeigen Risk-On Stimmung.")

if btc_change > 0:
    summary.append("Bitcoin bestätigt Risikoappetit.")

if volatility < 1:
    summary.append("Volatilität bleibt niedrig – ruhiges Marktumfeld.")

if volatility > 1.5:
    summary.append("Erhöhte Marktvolatilität deutet auf Unsicherheit hin.")

if up > down:
    summary.append("Mehr SMI Aktien steigen als fallen – positive Marktbreite.")

if down > up:
    summary.append("Mehr SMI Aktien fallen als steigen – Markt unter Druck.")

for line in summary:
    st.write("•", line)
