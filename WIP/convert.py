import os, sys
sys.path.append('../application')
import binance_client
import time
from binance.enums import *
from binance.helpers import round_step_size
import application_config as cfg
from binance.exceptions import BinanceAPIException
import traceback


def create_indirect_order(client, buy_symbol, buy_gbp_pice, quantity_to_buy, intermediary_symbol, intermediary_crypto_price, convert_amount, sell_sybmol, sell_gbp_price): 

    print(quantity_to_buy)
    print(buy_symbol)
    print(buy_gbp_pice)

    buy_order = client.create_test_order(
        symbol=buy_symbol,
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_FOK,
        quantity=quantity_to_buy,
        price=buy_gbp_pice)

    print(buy_order)
    print(intermediary_symbol)
    print(intermediary_crypto_price)
    print(convert_amount)
    

    convert_order = client.create_test_order(
        symbol=intermediary_symbol,
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=convert_amount,
        price=intermediary_crypto_price)

    print(convert_order)

    sell_order = client.create_test_order(
        symbol=sell_sybmol,
        side=SIDE_SELL,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=convert_amount,
        price=sell_gbp_price)

    print(sell_order)


def main(client, cryptos):
    for crypto in cryptos:
        for intermediary_crypto in cryptos[crypto]:
            print("--------------------------------")
            print("Checking pair: ", crypto, intermediary_crypto)
            

            buy_symbol = intermediary_crypto+"USDT"
            intermediary_symbol = crypto+intermediary_crypto
            sell_sybmol = crypto+"USDT"
            
            sell_gbp_price = float(client.get_symbol_ticker(symbol=sell_sybmol).get("price"))
            buy_gbp_pice = float(client.get_symbol_ticker(symbol=buy_symbol).get("price"))
            intermediary_crypto_price = float(client.get_symbol_ticker(symbol=intermediary_symbol).get("price"))
            

            indirect_gbp_price = intermediary_crypto_price * buy_gbp_pice


            if indirect_gbp_price/sell_gbp_price < 0.999:
                print("Cheaper")
                print("difference", indirect_gbp_price/sell_gbp_price )
                print(buy_symbol, buy_gbp_pice)
                print("Indirect price", indirect_gbp_price)
                print(sell_sybmol, sell_gbp_price)
                print(intermediary_symbol, intermediary_crypto_price)
            elif indirect_gbp_price/sell_gbp_price > 1.001:            
                print("More expensive")
                print("difference", indirect_gbp_price/sell_gbp_price )
                print(buy_symbol, buy_gbp_pice)
                print(sell_sybmol, sell_gbp_price)
                print("Indirect price", indirect_gbp_price)
                print(intermediary_symbol, intermediary_crypto_price)
            print(intermediary_symbol, intermediary_crypto_price)


if __name__ == '__main__':
    intermediary_cryptos = [ "BNB" ]


    client = binance_client.get_client(cfg.api_key,cfg.api_secret)

    cryptos = {
        #"ETH": [
        #    "BTC",
        #],
        "ADA": [
            "BTC",
            "ETH",
        ],
        #"BNB": [
        #    "BTC",
        #    "ETH",
        #],
        #"MATIC": [
        #    "BTC",
        #    "BNB",
        #]
    }
    #main(client, cryptos)
    while True:
        main(client, cryptos)