import yfinance as yf
import pandas as pd

SLI = [
"ABBN.SW","ADEN.SW","ALC.SW","BAER.SW","GEBN.SW",
"GIVN.SW","HOLN.SW","KNIN.SW","LONN.SW","LOGN.SW",
"NESN.SW","NOVN.SW","PGHN.SW","RICN.SW","ROG.SW",
"SREN.SW","SIKA.SW","SOON.SW","STMN.SW","TEMN.SW",
"UBSG.SW","ZURN.SW"
]

CRYPTO={
"Bitcoin":"BTC-EUR",
"Ethereum":"ETH-EUR",
"Cardano":"ADA-EUR",
"Solana":"SOL-EUR"
}

COMMODITIES={
"Oil":"CL=F",
"Gold":"GC=F",
"Silver":"SI=F"
}

INDICES={
"SMI":"^SSMI",
"S&P500":"^GSPC",
"NASDAQ":"^IXIC",
"DOW":"^DJI",
"DAX":"^GDAXI",
"CAC40":"^FCHI",
"FTSE100":"^FTSE",
"NIKKEI":"^N225",
"SHANGHAI":"000001.SS",
"HANGSENG":"^HSI",
"SYDNEY":"^AXJO"
}

def load_stocks():

    rows=[]

    for ticker in SLI:

        try:

            stock=yf.Ticker(ticker)
            hist=stock.history(period="1mo")

            price=hist["Close"].iloc[-1]
            prev=hist["Close"].iloc[-2]

            day=((price-prev)/prev)*100
            month=((price-hist["Close"].iloc[0])/hist["Close"].iloc[0])*100

            info=stock.info
            div=info.get("dividendYield",0)

            if div and div<1:
                div=div*100

            rows.append({
            "Ticker":ticker.replace(".SW",""),
            "Preis":round(price,2),
            "Tag %":round(day,2),
            "Monat %":round(month,2),
            "Dividende %":round(div,2)
            })

        except:
            pass

    return pd.DataFrame(rows)

def load_assets(dic):

    rows=[]

    for name,ticker in dic.items():

        try:

            data=yf.Ticker(ticker).history(period="1mo")

            price=data["Close"].iloc[-1]
            prev=data["Close"].iloc[-2]

            day=((price-prev)/prev)*100
            month=((price-data["Close"].iloc[0])/data["Close"].iloc[0])*100

            rows.append({
            "Asset":name,
            "Preis":round(price,2),
            "Tag %":round(day,2),
            "Monat %":round(month,2)
            })

        except:
            pass

    return pd.DataFrame(rows)

stocks=load_stocks()
crypto=load_assets(CRYPTO)
commodities=load_assets(COMMODITIES)
indices=load_assets(INDICES)

stocks.to_csv("stocks.csv",index=False)
crypto.to_csv("crypto.csv",index=False)
commodities.to_csv("commodities.csv",index=False)
indices.to_csv("indices.csv",index=False)
