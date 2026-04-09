#!/bin/bash

pip3 install yfinance pandas streamlit plotly --quiet

cat > market << 'RUN'
#!/bin/bash
cd ~/market_dashboard
python3 market_report.py
streamlit run dashboard.py
RUN

chmod +x market

echo "Installation abgeschlossen."
echo "Starte das Dashboard mit:"
echo "./market"
