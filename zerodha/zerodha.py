from disco import nifty100, notify, tabulate
import json
import websocket
import urllib.parse
import requests
import time
import dotenv as dt
import datetime


config = dt.dotenv_values(".env_zerodha")
enctoken = ''
mode = 'quote'

login_payload = {
    'user_id': config['user_id'],
    'password': config['password']
}
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

nifty100tokens, nifty100names = nifty100()


def quote(hex):
    no_of_packets = int(hex[0:4], 16)
    if no_of_packets != 0:
        # LTP Packet size is usually fixed.
        quote_size = 92
        # Seperating the number of packets info from hex.
        det = hex[4:]
        # Splitting the data equally by number of packets.
        tickers_data = [det[i:i+quote_size]
                        for i in range(0, len(det), quote_size)]
        # print(tickers_data)
        table_data = []
        for ticker in tickers_data:
            #     # Checking the packet size match or not with every packet.
            packet_size = int(ticker[0:4], 16)*2
            # print(packet_size)
            if packet_size == quote_size-4:
                data = ticker[4:]
                token = int(data[0:8], 16)
                ltp = int(data[8:16], 16)/100
                ltq = int(data[16:24], 16)
                day_open = int(data[56:64], 16)/100
                prev_day_close = int(data[80:88], 16)/100
                table_data.append(
                    {"token": token, "prevDayClose": prev_day_close, "dayOpen": day_open, "ltp": ltp})
                if ltp*ltq >= 20000000:
                    notify(token, ltp, ltq, nifty100names)
                # print('Token', int(data[0:8], 16))
                # print('LTP', int(data[8:16], 16)/100)
                # print('Last Traded QTY', int(data[16:24], 16))
                # print('Avg Traded Price', int(data[24:32], 16)/100)
                # print('Day Vol', int(data[32:40], 16))
                # print('Total Buy qty', int(data[40:48], 16))
                # print('Total Sell qty', int(data[48:56], 16))
                # print('Day Open', int(data[56:64], 16)/100)
                # print('Day High', int(data[64:72], 16)/100)
                # print('Day Low', int(data[72:80], 16)/100)
                # print('Prev Close', int(data[80:88], 16)/100)
            else:
                print('Data Packet Error!')
        tabulate(table_data, nifty100names)


def ltpc(hex):
    # Works for stocks and indexs as well.
    # Calculating number of packets in the binary message.
    no_of_packets = int(hex[0:4], 16)
    if no_of_packets != 0:
        # LTP Packet size is usually fixed=>(12(LTP Packet)*2(For Hexadecimal)+4(LTP Packet Size)).
        ltp_size = 28
        # Seperating the number of packets info from hex.
        det = hex[4:]
        # Splitting the data equally by number of packets.
        tickers_data = [det[i:i+ltp_size]
                        for i in range(0, len(det), ltp_size)]
        for ticker in tickers_data:
            # Checking the packet size match or not with every packet.
            packet_size = int(ticker[0:4], 16)*2
            if packet_size == ltp_size-4:
                data = ticker[4:]
                print('Token', int(data[0:8], 16))
                print('LTP', int(data[8:16], 16)/100)
                print('Prev Close', int(data[16:24], 16)/100)
            else:
                print('Data Packet Error!')


def on_open(ws):
    # det1 = {'a': 'subscribe', 'v': [6401, 13478914]}
    # det2 = {'a': 'mode', 'v': [mode, [6401]]}
    det2 = {'a': 'mode', 'v': [mode, nifty100tokens]}
    print('Opened')
    # ws.send(json.dumps(det1))
    ws.send(json.dumps(det2))


def on_message(ws, message):
    if isinstance(message, str):
        print('Recieved String:', message)
    else:
        # print(f'Raw Data Recieved :{message}\n')
        datastr = message.hex()
        # print(f'Hexa: {datastr}')
        print(f'Data recieved {datetime.datetime.now()}')
        if mode == 'ltpc':
            ltpc(datastr)
        else:
            quote(datastr)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def hello(enctoken):
    epoch_time = int(time.time()*1000)
    websocket_payload = {
        'api_key': config['api_key'],
        'user_id': config['user_id'],
        'enctoken': enctoken,
        'uid': f'{epoch_time}'
    }
    query = urllib.parse.urlencode(websocket_payload)
    ws_url = f"{config['webSock_url']}{query}"
    print(ws_url)
    ws = websocket.WebSocketApp(
        ws_url, on_open=on_open, on_message=on_message, on_close=on_close)
    ws.run_forever()
    # ws.send(json.dumps({"a": "subscribe", "v": [18213122]}))
    # ws.send(json.dumps({"a": "mode", "v": ["ltpc", [18213122]]}))
    # {"a": "unsubscribe", "v": [18213122]}


def zerodha():
    with requests.Session() as s:
        login = s.post(config['login_url'],
                       data=login_payload, headers=headers)
        print(login.json())
        if login.status_code == 200:
            log_response = login.json()
            two_fa_payload = {
                'user_id': config['user_id'],
                'request_id': log_response['data']['request_id'],
                'twofa_value': config['twofa_value']
            }
            two_fa = s.post(config['twofa_url'],
                            data=two_fa_payload, headers=headers)
            enctoken = two_fa.cookies['enctoken']
            hello(enctoken)
            final_headers = {
                'authorization': f'enctoken {enctoken}'
            }

            # mg = s.get(config['margins_url'], headers=final_headers)
            # print(mg.json())
        else:
            print(login.status_code)


zerodha()
