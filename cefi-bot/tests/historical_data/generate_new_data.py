import os
import json
from binance.client import Client

api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

client = Client(api_key, api_secret)

#bars = client.get_historical_klines('BTCUSDT', '1m', "30 days ago UTC")

#bars = client.get_historical_klines('BTCGBP', '3m', "1 days ago UTC")
#bars = client.get_historical_klines('BTCUSDT', '3m', "12 hours ago UTC")
#bars = client.get_historical_klines('BTCGBP', '1m', "1 Jan, 2021")


crypto  = "ETH"
span = "3m"
duration = "4 days"

bars = client.get_historical_klines(crypto+'USDT', span, duration +" ago UTC")


with open('dataset.json', 'w') as e:
    json.dump(bars, e)

#btc_bars = client.get_historical_klines('BTCUSDT', span, duration +" ago UTC")
#with open('btc_dataset.json', 'w') as e:
#    json.dump(btc_bars, e)
