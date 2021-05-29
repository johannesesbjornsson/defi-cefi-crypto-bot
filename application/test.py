import os
import json
import main
import binance_client


def get_test_set_hours():
    with open('btc_bars_last_hour.json') as f:
        d = json.load(f)
    return d
def get_test_set_year():
    with open('btc_bars.json') as f:
        d = json.load(f)
    return d

def get_price(data,asset):    
    return data[len(data)-1][4]


client = binance_client.get_client()
depth = client.get_order_book(symbol='XRPGBP', limit=5000)
current_price = float(client.get_symbol_ticker(symbol="BTCGBP").get("price"))
total_bids = 0.00
for trade in depth["bids"]:
    total_bids += float(trade[0])
    

print("---")
for trade in depth["asks"]:
    ask_evalutation = float(trade[0]) / float(trade[1])
    if ask_evalutation > current_price:
        print(ask_evalutation)
print(total_bids)
print(current_price)
print(len(depth["asks"]))
print(len(depth["bids"]))