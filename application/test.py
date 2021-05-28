import os
import json


def get_test_set_hours():
    with open('btc_bars_last_hour.json') as f:
        d = json.load(f)
    return d
def get_test_set_year():
    with open('btc_bars.json') as f:
        d = json.load(f)
    return d

def get_price(data,asset):    
    return data[len(data)-1][4]
    #return {'symbol': 'BTCGBP', 'price': 20035.94000000}