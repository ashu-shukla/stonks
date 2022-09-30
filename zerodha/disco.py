import json
import pandas as pd
from websocket import create_connection
import pprint
from discord_webhook import DiscordWebhook


filtered = pd.DataFrame()


def informServer(wss, msg):
    ws = create_connection(wss)
    print("Sending to internal server...")
    ws.send(msg)
    print("Sent")
    print("Receiving...")
    result = ws.recv()
    print(result)
    ws.close()


def nifty100():
    kite_nse_list = pd.read_csv("https://api.kite.trade/instruments/NSE")
    nse_nifty_100 = pd.read_csv(
        "https://archives.nseindia.com/content/indices/ind_nifty100list.csv")
    # print(kite_nse_list, "\n")
    # print(nse_nifty_100, "\n")

    result = kite_nse_list[kite_nse_list['tradingsymbol'].isin(
        nse_nifty_100['Symbol'])]
    filtered = result[['instrument_token', 'tradingsymbol', 'name']]
    # print(filtered['instrument_token'].to_numpy().ravel())
    return filtered['instrument_token'].to_numpy().tolist(), filtered


def getInstrument(token, df):
    # print(df)
    return df.loc[df['instrument_token'] == token]
    # return filtered.loc[filtered['instrument_token'] == token]


def notify(token, ltp, ltq, df):
    discord_url = "https://discord.com/api/webhooks/878985323009425468/1kUcjWjnB5UJTbMaUV_Pfmt_lSACqagVwq37GhwzJXJWMEFAIDWvjz5uWhzrkS-iCQBq"
    # print(token)
    instrument_info = getInstrument(token, df)
    company_name = instrument_info.iloc[0]['name']
    content = f'{company_name}: Trade above 2cr seen== {ltp*ltq}'
    webhook = DiscordWebhook(
        url=discord_url, rate_limit_retry=True, content=content)
    response = webhook.execute()


def tabulate(tableData, nifty100names):
    # print(tableData)
    # row = {token:token, prevDayClose:pdc, dayOpen:do, "ltp":ltp}
    for row in tableData:
        instrument_info = getInstrument(row['token'], nifty100names)
        # instrument_info = ['instrument_token', 'tradingsymbol', 'name']
        company_name = instrument_info.iloc[0]['name']
        company_symbol = instrument_info.iloc[0]['tradingsymbol']
        row["name"] = company_name
        row["symbol"] = company_symbol
        # gap_percent = round((row[2]-row[1])/row[1]*100, 2)
        # row.append(gap_percent)

    # tableData.sort(key=lambda x: x[6])
    pprint.pprint(tableData)
    informServer("ws://127.0.0.1:13254",
                 json.dumps({"event": "tickers", "data": tableData}))
# nifty100()
