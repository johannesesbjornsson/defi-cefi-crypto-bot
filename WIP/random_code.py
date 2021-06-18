import os, sys
import json
import datetime
sys.path.append('../application')
import binance_client
import time
from binance.helpers import round_step_size
import application_config as cfg

# symbol = "ETHGBP"

# client = binance_client.get_client()
# current_price = float(client.get_symbol_ticker(symbol=symbol).get("price"))
# depth = client.get_order_book(symbol=symbol, limit=1000)
# total_bids = 0.00
# for trade in depth["bids"]:
#     bid_price = float(trade[0])
#     bid_amount = float(trade[1])
#     off_market_price = bid_price/current_price
#     if off_market_price > 0.99 and off_market_price < 1.01:
#         total_bids += bid_amount

# total_ask = 0.00
# for trade in depth["asks"]:
#     ask_price = float(trade[0])
#     ask_amount = float(trade[1])
#     off_market_price = ask_price/current_price
#     if off_market_price > 0.99 and off_market_price < 1.01:
#         total_ask += ask_amount        

# print("Selling qty",total_ask)
# print("buying qty",total_bids)
# print(total_ask/total_bids)
# print(current_price)
# if total_ask/total_bids < 0.80:
#     print("Price will rise")
# elif total_ask/total_bids > 1.20:
#     print("Price will decrease")
# else:
#     print("Market stable")
# time.sleep(15)
# current_price = float(client.get_symbol_ticker(symbol=symbol).get("price"))
# print(current_price)

client = binance_client.get_client(cfg.api_key,cfg.api_secret)

asset_object = binance_client.Asset(client,"ADA",2)

import functools



class Test(object):
    def __init__(self, val):
        self.val = val

    @catch_exception
    def calc():
        return self.val / 0

t = Test(3)
t.calc()