import os, sys
sys.path.append('../application')
import binance_client
import time
from binance.enums import *
from binance.helpers import round_step_size
import application_config as cfg
from binance.exceptions import BinanceAPIException
import traceback

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
            

            if intermediary_crypto == "USDT":
                buy_symbol = "GBPUSDT"
                intermediary_symbol = crypto+"USDT"
                sell_sybmol = crypto+"GBP" 
            else:
                buy_symbol = intermediary_crypto+"GBP"
                intermediary_symbol = crypto+intermediary_crypto
                sell_sybmol = crypto+"GBP"
            
            sell_gbp_price = float(client.get_symbol_ticker(symbol=sell_sybmol).get("price"))
            buy_gbp_pice = float(client.get_symbol_ticker(symbol=buy_symbol).get("price"))
            intermediary_crypto_price = float(client.get_symbol_ticker(symbol=intermediary_symbol).get("price"))
            

            if intermediary_crypto == "USDT":
                indirect_gbp_price = intermediary_crypto_price / buy_gbp_pice 
            else:
                indirect_gbp_price = intermediary_crypto_price * buy_gbp_pice

            if indirect_gbp_price/sell_gbp_price < 0.9999:
                print("Cheaper")
                print("GBP price: ",sell_gbp_price)
                print("GBP price for intermediary: ",buy_gbp_pice)
                print("Indirect GBP price: ", indirect_gbp_price)
                print("Price difference: " ,indirect_gbp_price/sell_gbp_price)
                quantity_to_buy = round_step_size(50/buy_gbp_pice, cfg.precision_dict[intermediary_crypto]["qty_precision"])
                convert_amount = round_step_size(quantity_to_buy * intermediary_crypto_price, cfg.precision_dict[crypto]["qty_precision"])
                print("amount to convert ", quantity_to_buy /intermediary_crypto_price)
                create_indirect_order(client, buy_symbol, buy_gbp_pice, quantity_to_buy, intermediary_symbol, intermediary_crypto_price, convert_amount, sell_sybmol, sell_gbp_price)
            elif indirect_gbp_price/sell_gbp_price > 1.002:
                print("More expensive")
                print("GBP price: ",sell_gbp_price)
                print("GBP price for intermediary: ",buy_gbp_pice)
                print("Indirect GBP price: ", indirect_gbp_price)
                print("Price difference: " ,indirect_gbp_price/sell_gbp_price)



if __name__ == '__main__':
    intermediary_cryptos = [ "BNB" ]


    client = binance_client.get_client(cfg.api_key,cfg.api_secret)

    cryptos = {
        "ETH": [
            "BTC",
            "USDT"
        ],
        "ADA": [
            "BTC",
            "ETH",
            "USDT"
        ],
        "BNB": [
            "BTC",
            "ETH",
            "USDT"
        ]
    }
    while True:
        main(client, cryptos)