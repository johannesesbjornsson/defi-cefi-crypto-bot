import os
import json
import main
import logic
import datetime
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


# symbol = "BTCUSDT"
# #symbol = "XRPUSDT"
# client = binance_client.get_client()
# depth = client.get_order_book(symbol=symbol, limit=5000)
# current_price = float(client.get_symbol_ticker(symbol=symbol).get("price"))
# total_bid_volume = 0.00
# i = 0
# for trade in depth["bids"]:
    
#     if float(trade[0]) < (current_price * 1.05) and float(trade[0]) > (current_price * 0.95):
#         total_bid_volume += float(trade[0]) * float(trade[1])
#         print(trade)
#         i += 1

# print("--------------")

# total_ask_volume = 0.00
# ii = 0
# for trade in depth["asks"]:
    
#     if float(trade[0]) < (current_price * 1.05) and float(trade[0]) > (current_price * 0.95):
#         total_ask_volume += float(trade[0]) * float(trade[1])
#         print(trade)
#         ii += 1

# print(i, ii)
# print(current_price)
# print(total_bid_volume)
# print(total_ask_volume)
# print(len(depth["bids"]))
# print(len(depth["asks"]))

asset = "ETH"



client = binance_client.get_client()
depth = client.get_order_book(symbol=asset+"GBP", limit=10)
for trade in depth["bids"]:
    print(trade)
current_price = binance_client.get_price(client,asset)
asset_amount = 50
#print(client.get_symbol_info('BTCGBP'))

binance_client.test_buy_asset(client,asset,asset_amount,current_price,5)
binance_client.test_sell_asset(client,asset,asset_amount,current_price,5)
