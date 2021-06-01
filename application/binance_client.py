import os
import json
from binance.client import Client
import math
from binance.enums import *
from binance.helpers import round_step_size



def get_client():
    api_key = os.environ.get('binance_api')
    api_secret = os.environ.get('binance_secret')

    client = Client(api_key, api_secret)
    return client

def get_last_hours_of_data(client, asset):
    data = client.get_historical_klines(asset+'GBP', '1m', "3 hours ago GMT")
    return data

def get_last_weeks_of_data(client, asset):
    data = client.get_historical_klines(asset+'GBP', '1h', "7 days ago GMT")
    return data

def get_price(client,asset):
    current_price = float(client.get_symbol_ticker(symbol=asset+"GBP").get("price"))
    return current_price


def buy_asset(client,asset,amount,current_price,decimals=6):
    print("Buying", asset)
    position = amount / current_price
    position_to_use = round_down(position,decimals)
    
    price_to_use = round_down((current_price * 0.996),2)

    order = client.create_order(
        symbol=asset+"GBP",
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=str(position_to_use),
        price=str(price_to_use))
        
    return order

def sell_asset(client,asset,amount,current_price,decimals=6):
    print("Selling", asset)
    price_to_use = round_down((current_price * 1.004),2)

    order = client.create_order(
        symbol=asset+"GBP",
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=amount,
        price=str(price_to_use))

    return order

def test_buy_asset(client,asset,amount,current_price,decimals=6):
    print("Buying", asset)
    position = amount / current_price
    position_to_use = round_down(position,decimals)
    
    price_to_use = round_down((current_price * 0.996),2)

    order = client.create_test_order(
        symbol=asset+"GBP",
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=str(position_to_use),
        price=str(price_to_use))
        
    return order

def test_sell_asset(client,asset,amount,current_price,decimals=6):
    print("Selling", asset)
    price_to_use = round_down((current_price * 1.004),2)

    order = client.create_test_order(
        symbol=asset+"GBP",
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=amount,
        price=str(price_to_use))

    return order

def get_asset_amount(client, asset,decimals=6):
    asset = float(client.get_asset_balance(asset=asset).get("free"))
    return round_down(asset,decimals)

def round_down(n, decimals):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

def get_orders(client, asset):
    orders = client.get_all_orders(symbol=asset+'GBP', limit=10)

    return orders

