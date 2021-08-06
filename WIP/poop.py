import os, sys
sys.path.append('../application')
import binance_client
import time
import json
from binance.enums import *
from binance.helpers import round_step_size
import application_config as cfg
from binance.exceptions import BinanceAPIException
import traceback


client = binance_client.get_client(cfg.api_key,cfg.api_secret)

#sell_usdt_price = float(client.get_symbol_ticker(symbol="ETHUSDT").get("price"))
#gbp_ust_price = float(client.get_symbol_ticker(symbol="GBPUSDT").get("price"))
#buy_gbp_price = float(client.get_symbol_ticker(symbol="ETHGBP").get("price"))
#print(sell_usdt_price)
#print(gbp_ust_price)
#print(sell_usdt_price/gbp_ust_price)
#print(buy_gbp_price)

#asset_object = binance_client.Asset(client,"BNB",purchase_amount=50,currency="ETH")
orders = client.get_all_orders(symbol="ETHGBP", limit=40)
for order in orders:
    print(order) 