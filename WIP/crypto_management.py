import os, sys
sys.path.append('../application')
from binance.client import Client
from binance.helpers import round_step_size
from binance.enums import *
import application_config as cfg
import math


def get_usd_price(client,currency):
    price_usd = float(client.get_symbol_ticker(symbol=currency+"USDT").get("price"))
    return price_usd

def round_down(n, precision):
        multiplier = 10 ** precision
        return math.floor(n * multiplier) / multiplier

def validate_input(currency,action):
    if not currency.upper() in cfg.precision_dict:
        raise ValueError("unknown currency")
    if action != "sell" and action != "buy":
        raise ValueError("action must be buy or sell")

    return currency.upper()

def validate_price_to_use(currency,price,price_input_raw,action):
    if price_input_raw == "":
        price_position = 1
    else:
        price_input = float(price_input_raw)
        if action == "buy" and price_input > price:
            raise ValueError("Price must be lower than market value")
        if action == "sell" and price_input < price:
            raise ValueError("Price must be higher than market value")
        if price_input/price < 0.8 or price_input/price > 1.2:
            raise ValueError("Price difference too high")
        price_position = price_input/price


    price_gbp = float(client.get_symbol_ticker(symbol=currency+"GBP").get("price"))
    
    price_to_use = round_step_size(price_gbp * price_position, 0.000001)

    return price_to_use

def validate_amount_to_use(amount_worth_input,currency):
    if amount_worth_input == "":
        amount_worth_input = 100
    amount_worth = int(amount_worth_input)
    if amount_worth > 200:
        raise ValueError("Too much")
    if amount_worth < 40:
        raise ValueError("Too little")


    price_gbp = float(client.get_symbol_ticker(symbol=currency+"GBP").get("price"))
    position =  amount_worth / price_gbp
    
    position_to_buy = round_down(position,cfg.precision_dict[currency]["precision"])
    return position_to_buy

def create_order(client,currency,action,amount,price_to_use):
    print(price_to_use)
    print(amount)
    print(action)
    order = client.create_test_order(
        symbol=currency+"GBP",
        side=action,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=amount,
        price=price_to_use)
        
    return order

if __name__ == '__main__':
    currency = sys.argv[1]
    action = sys.argv[2]
    currency = validate_input(currency,action)
    print (action, currency)

    client = Client(cfg.api_key,cfg.api_secret)
    price_usd = get_usd_price(client,currency)

    amount_worth_input = input("Amount worth to use (£100) ")
    amount_to_use = validate_amount_to_use(amount_worth_input,currency)


    price_input = input("Price to use (current market price "+str(price_usd)+") ")
    price_to_use = validate_price_to_use(currency,price_usd,price_input,action)
    
    order = create_order(client,currency,action,amount_to_use,price_to_use)

    print(order)

