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
print(client.get_symbol_ticker(symbol="BTCGBP"))   
exhange_info = client.get_exchange_info()
for symbol in exhange_info["symbols"]:
    
    if symbol["symbol"] == "ADABTC":
        #print(symbol)
        lot_size = dict(("lot_size", item["stepSize"]) for item in symbol["filters"] if item["filterType"] == "LOT_SIZE")["lot_size"]
        
        print(lot_size)
        #keys = [item['id'] for item in initial_list]
        print(json.dumps(symbol, indent=4, sort_keys=True))