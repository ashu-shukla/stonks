
adnani_get_UC_LC = {"id": "6401", "a": "quote", "v": {"fields": [
    "lower_circuit_limit", "upper_circuit_limit", "expiry"], "tokens": [6401]}}
response = {"type": "quote", "id": "6401", "data": [[3344.7, 4087.9, 0]]}

new = b'\x00\x02\x00\x1c\x00\x03\xe9\t\x00\x1a\xe6\xa4\x00\x1b\n\xf3\x00\x1a\xc0\x9d\x00\x1a\xde\xc5\x00\x1b\t;\xff\xff\xddi\x00,\x00\x00\x19\x01\x00\x05\xab\xae\x00\x00\x002\x00\x05\xa0\xaf\x005C\xd4\x00\x00\x15\x81\x00\x00\x00\x00\x00\x05\x8d|\x00\x05\xb3[\x00\x05\x81e\x00\x05\x8d\xea'

dexa = '0001002c000019010005abae000000320005a0af003543d4000015810000000000058d7c0005b35b0005816500058dea'


data1 = b"\x00\x01\x00\x0c\x00\x03\xe9\t\x00\x1b`p\x00\x1b6'"
data1hex = '0001000c0003e909001b61a6001b3627'
data3 = b"\x00\x03\x00\x0c\x00\x04\x0b\t\x00\x00\x06\xff\x00\x00\x06\xec\x00\x0c\x00\x03\xe9\t\x00\x1b]\x91\x00\x1b6'\x00\x0c\x00\x02\xd4\x01\x00\x00]\xa2\x00\x00]\x16"
data3hex = '0003000c00040b09000006ff000006ec000c0003e909001b5d91001b3627000c0002d40100005da200005d16'
data2 = b"\x00\x02\x00\x0c\x00\x04\x0b\t\x00\x00\x06\xfe\x00\x00\x06\xec\x00\x0c\x00\x03\xe9\t\x00\x1b]K\x00\x1b6'"
data2hex = '0002000c00040b09000006fe000006ec000c0003e909001b5d4b001b3627'
data0 = b'\x00'
data0hex = '00'

hex = dexa
# Calculating number of packets in the binary message.
no_of_packets = int(hex[0:4], 16)
# LTP Packet size is usually fixed.
ltp_size = 92
# Seperating the number of packets info from hex.
det = hex[4:]
# Splitting the data equally by number of packets.
tickers_data = [det[i:i+ltp_size] for i in range(0, len(det), ltp_size)]
print(tickers_data)
for ticker in tickers_data:
    #     # Checking the packet size match or not with every packet.
    packet_size = int(ticker[0:4], 16)*2
    # print(packet_size)
    if packet_size == ltp_size-4:
        data = ticker[4:]
        print('Token', int(data[0:8], 16))
        print('LTP', int(data[8:16], 16)/100)
        print('Last Traded QTY', int(data[16:24], 16))
        print('Avg Traded Price', int(data[24:32], 16)/100)
        print('Day Vol', int(data[32:40], 16))
        print('Total Buy qty', int(data[40:48], 16))
        print('Day Open', int(data[48:64], 16)/100)
        print('Day High', int(data[64:72], 16)/100)
        print('Day Low', int(data[72:80], 16)/100)
        print('Prev Close', int(data[80:88], 16)/100)
