from websocket_server import WebsocketServer
import json


def new_client(client, server):
    print(client)
    # server.send_message(client, json.dumps(
    #     {"event": "connected", "data": "Hi"}))
    #     server.send_message_to_all("Hey all, a new client has joined us")


def extractMsg(client, server, message):
    print(message)
    server.send_message_to_all(message)


server = WebsocketServer(host='127.0.0.1', port=13254)
server.set_fn_new_client(new_client)
server.set_fn_message_received(extractMsg)
server.run_forever()
