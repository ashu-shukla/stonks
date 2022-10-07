import json
import pandas as pd
import requests
import pprint

import urllib.parse

filtered = pd.DataFrame()


def nifty100json():
    kite_nse_list = pd.read_csv("https://api.kite.trade/instruments/NSE")
    nse_nifty_100 = pd.read_csv(
        "https://archives.nseindia.com/content/indices/ind_nifty100list.csv")
    # print(kite_nse_list, "\n")
    # print(nse_nifty_100, "\n")
    result = kite_nse_list[kite_nse_list['tradingsymbol'].isin(
        nse_nifty_100['Symbol'])]
    filtered = result[['instrument_token', 'tradingsymbol', 'name']]
    # print(filtered.to_json(orient='records'))
    with open('data.json', 'w') as f:
        json.dump(filtered.to_dict(orient='records'), f)


def tradingview():
    with open('data.json', 'r') as f:
        data = json.load(f)
        for stock in data:
            payload = {
                'text': stock['tradingSymbol'],
                'hl': '1',
                'country': 'IN',
                'lang': 'en',
                'type': 'stock',
                'domain': 'production'
            }
            query = urllib.parse.urlencode(payload)
            url = "https://symbol-search.tradingview.com/s/?"
            ws_url = f"{url}{query}"
            # print(ws_url)
            res = requests.get(ws_url)
            print(stock['tradingSymbol'])
            symbolList = res.json()['symbols']
            for symbol in symbolList:
                # print(symbol)
                if symbol['symbol'] == f'<em>{stock["tradingSymbol"]}</em>' and symbol['exchange'] == "NSE" and symbol["type"] == "stock":
                    if 'logoid' in symbol:
                        print(stock['tradingSymbol'], symbol["logoid"])
                        stock["tdvLogoId"] = symbol["logoid"]
                        break
                    else:
                        print('No logo', stock['tradingSymbol'])
                        break
    with open('data.json', 'w') as f:
        json.dump(data, f)
