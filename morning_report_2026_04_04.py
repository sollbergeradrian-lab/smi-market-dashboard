from datetime import datetime
import pandas as pd
import os

today = datetime.now().strftime("%Y-%m-%d_%H-%M")

# Daten laden
stocks = pd.read_csv("stocks.csv")
crypto = pd.read_csv("crypto.csv")
indices = pd.read_csv("indices.csv")
commodities = pd.read_csv("commodities.csv")

# Marktstimmung berechnen
stocks["Tag %"] = pd.to_numeric(stocks["Tag %"], errors="coerce")

up = (stocks["Tag %"] > 0).sum()
down = (stocks["Tag %"] < 0).sum()

if up > down:
    sentiment = "Bullish"
elif down > up:
    sentiment = "Bearish"
else:
    sentiment = "Neutral"

# Marktkommentar
if sentiment == "Bullish":
    comment = "Der Schweizer Markt zeigt positive Marktbreite. Zyklische Aktien profitieren von globaler Stärke."
elif sentiment == "Bearish":
    comment = "Der Markt zeigt Schwäche. Defensive Titel könnten relative Stärke behalten."
else:
    comment = "Der Markt zeigt gemischte Signale ohne klare Richtung."

# Market Regime Detector
sp = float(indices.loc[indices.iloc[:,0] == "S&P500", "Tag %"].values[0])
nasdaq = float(indices.loc[indices.iloc[:,0] == "NASDAQ", "Tag %"].values[0])
bitcoin = float(crypto.loc[crypto.iloc[:,0] == "Bitcoin", "Tag %"].values[0])

score = 0

if sp > 0:
    score += 1
if nasdaq > 0:
    score += 1
if bitcoin > 0:
    score += 1

if score >= 2:
    regime = "Bull Market"
elif score == 1:
    regime = "Neutral Market"
else:
    regime = "Risk-Off Market"

# Market Insight Generator

insight = ""

if regime == "Bull Market":
    insight += "Globale Märkte zeigen Stärke. Risikoassets werden gekauft.\n"

if regime == "Risk-Off Market":
    insight += "Die globalen Märkte zeigen Risikoaversion. Investoren bevorzugen defensive Anlagen.\n"

# US Markt Einfluss
if sp > 0 and nasdaq > 0:
    insight += "US-Aktienmärkte unterstützen die globale Marktstimmung.\n"

if sp < 0 and nasdaq < 0:
    insight += "Schwache US-Märkte belasten die internationale Stimmung.\n"

# Bitcoin Risikoindikator
if bitcoin > 2:
    insight += "Starke Kryptomärkte signalisieren erhöhte Risikobereitschaft.\n"

if bitcoin < -2:
    insight += "Schwäche im Kryptomarkt deutet auf sinkende Risikobereitschaft hin.\n"

# Rohstoffe
oil = float(commodities.loc[commodities.iloc[:,0] == "Oil", "Tag %"].values[0])

if oil > 3:
    insight += "Deutlich steigende Ölpreise könnten Inflationsdruck erhöhen.\n"

if oil < -3:
    insight += "Fallende Energiepreise wirken potenziell inflationsdämpfend.\n"

# Top Movers
top_gainers = stocks.sort_values("Tag %", ascending=False).head(5)
top_losers = stocks.sort_values("Tag %").head(5)

# Report erstellen
report = f"""
# Swiss Market Morning Report

Datum: {today}

---

## SMI Marktstimmung
{sentiment}

### Marktkommentar
{comment}

## Market Regime
{regime}
"""

# Gewinner
report += "\n## Top Gewinner\n"

for _, row in top_gainers.iterrows():

    change = float(row["Tag %"])
    month = float(row["Monat %"])
    price = float(row["Preis"])

    if change > 0:
        symbol = "+"
    else:
        symbol = "-"

    report += f"- {row['Ticker']} {price:.2f} CHF {symbol}{change:.2f}% (Monat {month:.2f}%)\n"

# Verlierer
report += "\n## Top Verlierer\n"

for _, row in top_losers.iterrows():

    change = float(row["Tag %"])
    month = float(row["Monat %"])
    price = float(row["Preis"])

    if change > 0:
        symbol = "+"
    else:
        symbol = "-"

    report += f"- {row['Ticker']} {price:.2f} CHF {symbol}{change:.2f}% (Monat {month:.2f}%)\n"

# Globale Märkte
report += "\n## Globale Märkte\n"

for _, row in indices.iterrows():
    report += f"- {row.iloc[0]} {row['Tag %']}%\n"

# Krypto
report += "\n## Krypto\n"

for _, row in crypto.iterrows():

    name = row.iloc[0]
    price = float(row["Preis"])
    change = float(row["Tag %"])

    if change > 0:
        symbol = "+"
    else:
        symbol = "-"

    report += f"- {name} {price:.2f} USD ({symbol}{change:.2f}%)\n"

# Rohstoffe
report += "\n## Rohstoffe\n"

for _, row in commodities.iterrows():

    name = row.iloc[0]
    price = float(row["Preis"])
    change = float(row["Tag %"])

    if change > 0:
        symbol = "+"
    else:
        symbol = "-"

    report += f"- {name} {price:.2f} USD ({symbol}{change:.2f}%)\n"

# temporäre Datei
temp_file = "/tmp/morning_report.txt"

with open(temp_file, "w") as f:
    f.write(report)

# PDF speichern
output = f"/Users/adi/Library/Mobile Documents/com~apple~CloudDocs/Market Reports/Swiss_Market_Report_{today}.pdf"

os.system(f"pandoc {temp_file} -o '{output}' -V geometry:margin=2cm")

print("Morning Report erstellt:", output)
