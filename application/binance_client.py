import os
import json
from binance.client import Client



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


def buy_asset(client,asset,amount,price):
    print("Buying", asset)
    position = amount / price
    position_to_use = str(position)[:-13]
    order = client.create_order(
        symbol=asset+"GBP",
        side="buy",
        type="market",
        quantity=position_to_use)
    return order

def sell_asset(client,asset,amount):
    print("Selling", asset)
    position_to_use = str(amount)[:-2]
    order = client.create_order(
        symbol=asset+"GBP",
        side="sell",
        type="market",
        quantity=position_to_use)
    return order

def buy_asset(client,asset,amount,price):
    print("Buying", asset)
    position = amount / price
    position_to_use = str(position)[:-13]
    order = client.create_test_order(
        symbol=asset+"GBP",
        side="buy",
        type="market",
        quantity=position_to_use)
    return order

def sell_asset(client,asset,amount):
    print("Selling", asset)
    position_to_use = str(amount)[:-2]
    order = client.create_test_order(
        symbol=asset+"GBP",
        side="sell",
        type="market",
        quantity=position_to_use)
    return order

def get_asset_amount(client, asset):
    asset = float(client.get_asset_balance(asset=asset).get("free"))
    return asset


