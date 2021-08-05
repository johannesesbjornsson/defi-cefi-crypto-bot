import os, sys
import json
import datetime
sys.path.append('../application')
import binance_client
import time
from binance.helpers import round_step_size
import application_config as cfg


def main(client, symbol):
    current_price = float(client.get_symbol_ticker(symbol=symbol).get("price"))
    depth = client.get_order_book(symbol=symbol, limit=1000)
    total_bids = 0.00
    price_increase = False
    price_decrease = False
    for trade in depth["bids"]:
        bid_price = float(trade[0])
        bid_amount = float(trade[1])
        off_market_price = bid_price/current_price
        #if off_market_price > 0.99 and off_market_price < 1.01:
        if off_market_price > 0.995:
            total_bids += bid_amount

    total_ask = 0.00
    for trade in depth["asks"]:
        ask_price = float(trade[0])
        ask_amount = float(trade[1])
        off_market_price = ask_price/current_price
        #if off_market_price > 0.99 and off_market_price < 1.01:
        if off_market_price < 1.015:
            total_ask += ask_amount        


    if total_ask/total_bids < 0.50:
        price_increase = True
        print("Prices will increase")
    elif total_ask/total_bids > 1.50:
        price_decrease = True
        print("Prices will decrease")
    else:
        print("Market stable")
        return True

    print("Selling qty",total_ask)
    print("buying qty",total_bids)
    print(current_price)
    
    for i in range(15):
        new_price = float(client.get_symbol_ticker(symbol=symbol).get("price"))
        print(new_price)
        time.sleep(1)

    if price_increase == True and new_price > current_price:
        print("Success, prices increased")
        if new_price/current_price > 1.001:
            print("Worthwhile")
        else:
            print("Not worthwhile")
    elif price_decrease == True and new_price < current_price:
        print("Success, prices decreased")
    else:
        print("Failed, prediction was wrong")
    print(new_price/current_price)
    print(new_price)

if __name__ == '__main__':
    symbol = "ADAUSDT"
    symbol = "ADABTC"
    client = binance_client.get_client(cfg.api_key,cfg.api_secret)
    while True:
        main(client,symbol)
        print("------------------")