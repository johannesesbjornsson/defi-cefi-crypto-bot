import os, sys
import json
import datetime
sys.path.append('../application')
import binance_client
import time
from binance.helpers import round_step_size


client = binance_client.get_client()


res = client.get_exchange_info()
currency_to_check = ["DOGE", "DOT", "LTC", "MATIC"]
#currency_to_check = ["DOGE"]
fiat = "GBP"

all_available_exchanges = {}
for currency in currency_to_check:
    crypto_exchanges_to_check = [currency+"BTC",currency+"ETH",currency+"BNB"]
    available_exchanges = []
    for info in res["symbols"]:
        symbol = info["symbol"]
        if symbol.startswith(currency) and symbol in crypto_exchanges_to_check and info["status"] == "TRADING":
            print(info)
            available_exchanges.append(symbol)
            
    
    all_available_exchanges[currency] = available_exchanges

for exchanges in all_available_exchanges:
    print(exchanges)
    print(all_available_exchanges[exchanges])



def create_indirect_order(asset_to_buy,buy_asset_with,buy_asset_with_worth,price_in_crypto):

    quantity_to_buy = round_step_size(30/buy_asset_with_worth, 0.0001)


    order = client.create_test_order(
        symbol=buy_asset_with+"GBP",
        side="buy",
        type="market",
        quantity=quantity_to_buy)

    quantity_to_buy =  round_step_size(buy_asset_with_worth * quantity_to_buy, 1)
    
    print(asset_to_buy+buy_asset_with)
    order = client.create_test_order(
        symbol=asset_to_buy+buy_asset_with,
        side="buy",
        type="market",
        quantity=quantity_to_buy)


for curreny in all_available_exchanges:
    print("-------------------")
    print("Comparing exchangerates for",curreny)
    for symbol in all_available_exchanges[curreny]:
        exchange = symbol[-3:]


        price_in_crypto = float(client.get_symbol_ticker(symbol=symbol).get("price"))
        fiat_price_of_other_crypto = float(client.get_symbol_ticker(symbol=exchange+fiat).get("price"))

        indirect_cost = fiat_price_of_other_crypto * price_in_crypto
        
        direct_cost = float(client.get_symbol_ticker(symbol=curreny+fiat).get("price"))
        

        if indirect_cost/direct_cost < 0.999:
            print(indirect_cost/direct_cost)
            create_indirect_order(curreny,exchange,fiat_price_of_other_crypto,price_in_crypto)



