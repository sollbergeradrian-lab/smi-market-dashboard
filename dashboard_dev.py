import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import os
from datetime import date
from fpdf import FPDF

def safe_history(ticker, period="2d"):

    try:
        data = yf.Ticker(ticker).history(period=period)

        if data is None or data.empty:
            return None

        return data

    except:
        return None


def clean_percent(x):

    try:
        return float(
            str(x)
            .replace("🟢","")
            .replace("🔴","")
            .replace("▲","")
            .replace("▼","")
            .replace("%","")
            .replace(",",".")
            .strip()
        )
    except:
        return 0

def trend(x):

    if x > 0:
        return f"🟢 ▲ {x:.2f}%"

    if x < 0:
        return f"🔴 ▼ {abs(x):.2f}%"

    return f"{x:.2f}%"

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
    data = safe_history(ticker)

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
    data = safe_history(ticker)

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

st.plotly_chart(fig, use_container_width=True, key="global_market_radar")

st.subheader("🌙 Overnight Futures Radar")

futures = {
"S&P500 Futures": "ES=F",
"NASDAQ Futures": "NQ=F",
"Oil": "CL=F",
"Gold": "GC=F",
"Bitcoin": "BTC-USD"
}

for name, ticker in futures.items():

    try:

        data = safe_history(ticker)

        if data is not None and len(data) >= 2:

            change = ((data["Close"].iloc[-1] / data["Close"].iloc[-2]) - 1) * 100

            st.write(f"**{name}**  {trend(change)}")

    except:

        pass

# Daten laden
stocks = pd.read_csv("stocks.csv")
crypto = pd.read_csv("crypto.csv")
indices = pd.read_csv("indices.csv")
commodities = pd.read_csv("commodities.csv")

# ---------- NUMERISCHE VERSION DER DATEN ----------

stocks_num = stocks.copy()

stocks_num["Tag_raw"] = stocks["Tag %"].apply(clean_percent)
stocks_num["Monat_raw"] = stocks["Monat %"].apply(clean_percent)

# Kopie für Sortierungen

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

    data = safe_history(ticker)

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

st.plotly_chart(fig1, use_container_width=True, key="heatmap")

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
    
st.subheader("🧠 Smart Money Radar")

moves = []

for i,row in stocks.iterrows():

    try:
        change = float(str(row["Tag %"]).replace("%","").replace("▲","").replace("▼","").replace("🟢","").replace("🔴",""))
        
        if abs(change) > 2:
            moves.append((row["Ticker"], change))

    except:
        pass

if len(moves) == 0:

    st.write("Keine ungewöhnlich starken Bewegungen")

else:

    for ticker,change in moves:

        st.write(ticker, trend(change))

st.subheader("🧠 SMI Liquidity Heatmap")

heatmap_data = stocks_num.copy()

heatmap_data = heatmap_data.sort_values("Tag_raw", ascending=False)

fig = px.bar(
    heatmap_data,
    x="Ticker",
    y="Tag_raw",
    color="Tag_raw",
    color_continuous_scale=["red","white","green"],
)

st.plotly_chart(fig2, use_container_width=True, key="liquidity")

st.subheader("⚠️ SMI Crash Risk Radar")

negatives = (stocks_num["Tag_raw"] < 0).sum()
positives = (stocks_num["Tag_raw"] > 0).sum()

big_losses = (stocks_num["Tag_raw"] < -2).sum()

avg_change = stocks_num["Tag_raw"].mean()

risk_score = 0

# Marktbreite
if negatives > positives:
    risk_score += 1

# viele starke Verluste
if big_losses >= 3:
    risk_score += 1

# Durchschnitt negativ
if avg_change < 0:
    risk_score += 1

# Bewertung

if risk_score == 0:
    st.success("🟢 Niedriges Risiko – Marktstruktur stabil")

elif risk_score == 1:
    st.warning("🟡 Leichte Schwäche im Markt")

elif risk_score == 2:
    st.warning("🟠 Risiko steigt – Marktbreite negativ")

else:
    st.error("🔴 Crash Risiko erhöht – viele Aktien unter Druck")

# Diagnose anzeigen
st.write("Marktbreite:", positives, "Gewinner /", negatives, "Verlierer")
st.write("Starke Verluste (>-2%):", big_losses)
st.write("Durchschnittliche Tagesperformance:", round(avg_change,2), "%")

# SMI Smart Money Radar
st.subheader("🧠 SMI Smart Money Radar")

smart_buy = stocks_num[(stocks_num["Tag_raw"] > 2) & (stocks_num["Monat_raw"] > 0)]
momentum = stocks_num[(stocks_num["Tag_raw"] > 1) & (stocks_num["Monat_raw"] > 3)]
weak = stocks_num[(stocks_num["Tag_raw"] < -2) & (stocks_num["Monat_raw"] < 0)]
reversal = stocks_num[(stocks_num["Tag_raw"] > 1) & (stocks_num["Monat_raw"] < -5)]

st.write("🐂 Smart Money Buy")

if smart_buy.empty:
    st.write("Keine starken institutionellen Käufe erkannt")
else:
    for _, row in smart_buy.head(3).iterrows():
        st.write(f"{row['Ticker']} ▲ {row['Tag_raw']:.2f}% (Monat {row['Monat_raw']:.2f}%)")

st.write("⚡ Momentum Aktien")

if momentum.empty:
    st.write("Kein starkes Momentum heute")
else:
    for _, row in momentum.head(3).iterrows():
        st.write(f"{row['Ticker']} ▲ {row['Tag_raw']:.2f}% (Monat {row['Monat_raw']:.2f}%)")

st.write("⚠ Schwache Aktien")

if weak.empty:
    st.write("Keine starken Verkäufe sichtbar")
else:
    for _, row in weak.head(3).iterrows():
        st.write(f"{row['Ticker']} ▼ {row['Tag_raw']:.2f}% (Monat {row['Monat_raw']:.2f}%)")

st.write("🔄 Kandidaten für eine Umkehrung")

if reversal.empty:
    st.write("Keine klaren Reversal-Signale")
else:
    for _, row in reversal.head(3).iterrows():
        st.write(f"{row['Ticker']} ▲ {row['Tag_raw']:.2f}% (Monat {row['Monat_raw']:.2f}%)")

st.subheader("🏦 Institutional Flow Tracker")

inst_candidates = stocks_num[
    (stocks_num["Tag_raw"] > 2) &
    (stocks_num["Monat_raw"] > 3)
]

inst_candidates = inst_candidates.sort_values("Tag_raw", ascending=False)

if inst_candidates.empty:

    st.write("Keine klaren institutionellen Käufe erkannt")

else:

    for _, row in inst_candidates.iterrows():

        st.write(
            f"🏦 **{row['Ticker']}** | Tag {row['Tag_raw']:+.2f}% | Monat {row['Monat_raw']:+.2f}%"
        )

st.subheader("🔄 Sector Rotation Radar")

sector_map = {
    "ABBN": "Industrials",
    "ADEN": "Industrials",
    "ALC": "Healthcare",
    "ROG": "Healthcare",
    "NOVN": "Healthcare",
    "ZURN": "Financials",
    "UBSG": "Financials",
    "CSGN": "Financials",
    "NESN": "Consumer Defensive",
    "CFR": "Luxury",
    "RICHEMONT": "Luxury",
    "HOLN": "Materials",
    "SIKA": "Materials",
    "LONN": "Chemicals",
    "GEBN": "Industrials"
}

stocks_num["Sector"] = stocks_num["Ticker"].map(sector_map)

sector_flow = (
    stocks_num
    .groupby("Sector")["Tag_raw"]
    .mean()
    .sort_values(ascending=False)
)

st.write("📈 Kapital fliesst in:")

for sector, value in sector_flow.head(3).items():
    st.write(f"🟢 {sector} ({value:+.2f}%)")

st.write("📉 Kapital verlässt:")

for sector, value in sector_flow.tail(3).items():
    st.write(f"🔴 {sector} ({value:+.2f}%)")

st.subheader("🧠 Institutional Flow Score")

stocks_num["Flow_Score"] = stocks_num["Tag_raw"] * 0.7 + stocks_num["Monat_raw"] * 0.3

top_inflow = stocks_num.sort_values("Flow_Score", ascending=False).head(5)
top_outflow = stocks_num.sort_values("Flow_Score").head(5)

st.write("📈 Stärkster Kapitalzufluss")

for _, row in top_inflow.iterrows():
    st.write(f"**{row['Ticker']}** | Flow Score {row['Flow_Score']:.2f} | Tag {row['Tag_raw']:+.2f}% | Monat {row['Monat_raw']:+.2f}%")

st.write("📉 Stärkster Kapitalabfluss")

for _, row in top_outflow.iterrows():
    st.write(f"**{row['Ticker']}** | Flow Score {row['Flow_Score']:.2f} | Tag {row['Tag_raw']:+.2f}% | Monat {row['Monat_raw']:+.2f}%")

# Gewinner / Verlierer
st.subheader("🚀 SLI Gewinner")
st.dataframe(stocks.sort_values("Tag %", ascending=False).head(10))

st.subheader("📉 SLI Verlierer")
st.dataframe(stocks.sort_values("Tag %").head(10))

st.subheader("🌊 SMI Kapitalfluss Radar")

inflow = stocks_num[stocks_num["Tag_raw"] > 0].sort_values("Tag_raw", ascending=False).head(3)
outflow = stocks_num[stocks_num["Tag_raw"] < 0].sort_values("Tag_raw").head(3)

st.write("📈 Kapital fliesst in:")

for _, row in inflow.iterrows():
    st.write(f"{row['Ticker']} 🟢 ▲ {row['Tag_raw']:.2f}%")

st.write("📉 Kapital verlässt:")

if outflow.empty:
    st.write("Keine signifikanten Kapitalabflüsse heute")
else:
    for _, row in outflow.iterrows():
        st.write(f"{row['Ticker']} 🔴 ▼ {abs(row['Tag_raw']):.2f}%")

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

def clean_percent(x):

    return float(
        str(x)
        .replace("🟢","")
        .replace("🔴","")
        .replace("▲","")
        .replace("▼","")
        .replace("%","")
        .replace(",",".")
        .strip()
    )

sp = clean_percent(indices.loc[indices.iloc[:,0] == "S&P500", "Tag %"].values[0])
nasdaq = clean_percent(indices.loc[indices.iloc[:,0] == "NASDAQ", "Tag %"].values[0])
btc = clean_percent(crypto.loc[crypto.iloc[:,0] == "Bitcoin", "Tag %"].values[0])
oil = clean_percent(commodities.loc[commodities.iloc[:,0] == "Oil", "Tag %"].values[0])

st.subheader("🧠 Automatische Markt-Zusammenfassung")

summary = []

if sp > 0 and nasdaq > 0:
    summary.append("US-Aktienmärkte zeigen Stärke.")

if sp < 0 and nasdaq < 0:
    summary.append("US-Aktienmärkte stehen unter Druck.")

if btc > 2:
    summary.append("Starke Kryptomärkte signalisieren hohe Risikobereitschaft.")

if btc < -2:
    summary.append("Schwäche im Kryptomarkt deutet auf sinkende Risikobereitschaft hin.")

if oil > 2:
    summary.append("Steigende Ölpreise könnten Inflationsdruck erhöhen.")

if oil < -2:
    summary.append("Fallende Energiepreise wirken potenziell inflationsdämpfend.")

# Falls nichts erkannt wird
if len(summary) == 0:
    summary.append("Die Märkte zeigen heute gemischte Signale ohne klare Richtung.")

for line in summary:
    st.write("•", line)

st.subheader("🧠 Market Regime AI")

# Daten holen
def clean_percent(x):

    return float(
        str(x)
        .replace("🟢","")
        .replace("🔴","")
        .replace("▲","")
        .replace("▼","")
        .replace("%","")
        .replace(",",".")
        .strip()
    )

sp = clean_percent(indices.loc[indices.iloc[:,0] == "S&P500", "Tag %"].values[0])
nasdaq = clean_percent(indices.loc[indices.iloc[:,0] == "NASDAQ", "Tag %"].values[0])
btc = clean_percent(crypto.loc[crypto.iloc[:,0] == "Bitcoin", "Tag %"].values[0])
oil = clean_percent(commodities.loc[commodities.iloc[:,0] == "Oil", "Tag %"].values[0])

score = 0

if sp > 0:
    score += 1

if nasdaq > 0:
    score += 1

if btc > 0:
    score += 1

if oil > 0:
    score += 1

st.subheader("🌍 Global Liquidity Radar")

signals = []

# Aktien Liquidität
if sp > 0 and nasdaq > 0:
    signals.append("🟢 Globale Aktienmärkte zeigen Liquiditätszufluss")

if sp < 0 and nasdaq < 0:
    signals.append("🔴 Aktienmärkte signalisieren Liquiditätsabfluss")

# Krypto Risikoindikator
if btc > 2:
    signals.append("🟢 Kryptomarkt signalisiert hohe Risikobereitschaft")

if btc < -2:
    signals.append("🔴 Kryptomarkt signalisiert sinkende Risikobereitschaft")

# Öl / Inflation
if oil > 3:
    signals.append("⚠ Steigende Ölpreise könnten Inflationsdruck erhöhen")

if oil < -3:
    signals.append("🟢 Sinkende Energiepreise wirken inflationsdämpfend")

# Falls keine starken Signale
if len(signals) == 0:
    signals.append("🟡 Liquiditätsumfeld aktuell neutral")

for s in signals:
    st.write(s)

st.subheader("⚠ Market Stress Index")

stress = 0

# Aktienmärkte
if sp < 0:
    stress += abs(sp)

if nasdaq < 0:
    stress += abs(nasdaq)

# Kryptomarkt
if btc < 0:
    stress += abs(btc)

# Öl als Inflationsrisiko
if oil > 2:
    stress += oil

# Score begrenzen
stress_score = min(int(stress * 10), 100)

# Bewertung
if stress_score < 20:
    status = "🟢 Niedriger Marktstress"

elif stress_score < 40:
    status = "🟡 Moderater Marktstress"

elif stress_score < 70:
    status = "🟠 Erhöhter Marktstress"

else:
    status = "🔴 Hoher Marktstress"


st.write(f"Market Stress Level: **{stress_score}%**")
st.write(status)

# Marktphase bestimmen
if score >= 3:
    regime = "🟢 Bull Market"

elif score == 2:
    regime = "🟡 Neutral Market"

elif score == 1:
    regime = "🔴 Risk-Off Market"

else:
    regime = "⚫ Panic Mode"


st.write("Aktuelle Marktphase:")
st.markdown(f"### {regime}")

# Rohstoffe aus Tabelle holen
oil = clean_percent(commodities.loc[commodities.iloc[:,0] == "Oil", "Tag %"].values[0])
gold = clean_percent(commodities.loc[commodities.iloc[:,0] == "Gold", "Tag %"].values[0])
btc = clean_percent(crypto.loc[crypto.iloc[:,0] == "Bitcoin", "Tag %"].values[0])

st.subheader("📄 Market Report")

if st.button("Generate Market Report"):

    report = f"""
Swiss Market Report
Datum: {today}

==============================
MARKET REGIME
==============================
{regime}

==============================
GLOBAL MARKETS
==============================
S&P500   {sp:.2f}%
NASDAQ   {nasdaq:.2f}%

==============================
CRYPTO
==============================
Bitcoin  {btc:.2f}%

==============================
COMMODITIES
==============================
Oil      {oil:.2f}%
Gold     {gold:.2f}%

==============================
SMI TOP MOVERS
==============================
"""

    top_gainers = stocks_num.sort_values("Tag_raw", ascending=False).head(3)

    for _, row in top_gainers.iterrows():
        report += f"{row['Ticker']}  {row['Tag_raw']:.2f}%\n"

    report += "\nSMI LOSERS\n\n"

    top_losers = stocks_num.sort_values("Tag_raw").head(3)

    for _, row in top_losers.iterrows():
        report += f"{row['Ticker']}  {row['Tag_raw']:.2f}%\n"

    report += "\nSMART MONEY FLOW\n\n"

    top_inflow = stocks_num.sort_values("Flow_Score", ascending=False).head(3)

    for _, row in top_inflow.iterrows():
        report += f"{row['Ticker']}  Score {row['Flow_Score']:.2f}\n"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in report.split("\n"):
        clean_line = (
            line.replace("🟢","")
            .replace("🔴","")
            .replace("▲","")
            .replace("▼","")
        )
        pdf.cell(0, 8, clean_line, ln=True)

    pdf.output("market_report.pdf")

    with open("market_report.pdf", "rb") as file:

        st.download_button(
            label="📥 Download Market Report PDF",
            data=file,
            file_name="Swiss_Market_Report.pdf",
            mime="application/pdf",
            key="download_market_report_pdf"
        )
