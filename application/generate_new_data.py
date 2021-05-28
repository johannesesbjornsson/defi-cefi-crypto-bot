import os
import json
from binance.client import Client

api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

client = Client(api_key, api_secret)

bars = client.get_historical_klines('BTCGBP', '1m', "3 hours ago UTC")
#bars = client.get_historical_klines('ETHGBP', '1m', "3 hours ago UTC")
#bars = client.get_historical_klines('BTCGBP', '1m', "1 Jan, 2021")

with open('btc_bars_last_hour.json', 'w') as e:
    json.dump(bars, e)