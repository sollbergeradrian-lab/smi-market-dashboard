from datetime import date
import os

today = date.today()

report_text = f"""
Swiss Market Report
Datum: {today}

Report automatisch generiert.

Datenquelle:
SMI Dashboard Analyse
"""

temp_file = "/tmp/market_report.txt"

with open(temp_file, "w") as f:
    f.write(report_text)

output = f"/Users/adi/Library/Mobile Documents/com~apple~CloudDocs/Market Reports/Swiss_Market_Report_{today}.pdf"

os.system(f"pandoc {temp_file} -o '{output}'")

print("PDF Report gespeichert in iCloud:", output)
