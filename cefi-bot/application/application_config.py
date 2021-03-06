import os

assets_to_check = {
    "ETHUSDT": {
        "medium_period_to_compare": 3,
        "short_period_to_compare": 10,
        "crypto": "ETH",
        "currency": "USDT",
        "double_downs": 1
    },   
}

cryptopairs = {
    "BNBETH": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "BNB",
        "currency": "ETH",
        "double_downs": 3,
    },
    "BNBBTC": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "BNB",
        "currency": "BTC",
        "double_downs": 3,
    },
    "ADABNB": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "ADA",
        "currency": "BNB",
        "double_downs": 3,
    },
    "ADABTC": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "ADA",
        "currency": "BTC",
        "double_downs": 3
    },
    "MATICBNB": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "MATIC",
        "currency": "BNB",
        "double_downs": 3
    },
    "MATICBTC": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "MATIC",
        "currency": "BTC",
        "precision" : 7,
        "double_downs": 3
    },
    "ETHBTC": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "ETH",
        "currency": "BTC",
        "double_downs": 3
    },   
}

precision_dict = {
    "BTC": {
        "precision" : 6,
        "price_precision": 0.01,
        "qty_precision": 0.000001
    },
    "ETH": {
        "precision" : 4,
        "price_precision": 0.01,
        "qty_precision": 0.0001
    },
    "BNB": {
        "precision" : 4,
        "price_precision": 0.01,
        "qty_precision": 0.0001
    },
    "XRP": {
        "precision" : 1,
        "price_precision": 0.000001,
        "qty_precision": 0.01
    },
    "ADA": {
        "precision" : 1,
        "price_precision": 0.000001,
        "qty_precision": 0.01
    },    
    "MATIC": {
        "precision" : 1,
        "price_precision": 0.000001,
        "qty_precision": 0.01
    },
}

api_key = os.environ['binance_api']
api_secret = os.environ['binance_secret']
email_api_key = os.environ['email_api_key']