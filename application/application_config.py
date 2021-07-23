import os

assets_to_check = {
    "BTC": {
        "crypto": "BTC",
        "currency": "GBP",
        "precision" : 6,
        "amount": 0.005 
    },
    "ETH": {
        "crypto": "ETH",
        "currency": "GBP",
        "precision" : 4,
        "amount": 0.05 
    },
    "BNB": {
        "crypto": "BNB",
        "currency": "GBP",
        "precision" : 4,
        "amount": 0.05 
    },   
}

cryptopairs = {
    "BNBETH": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "BNB",
        "currency": "ETH",
        "precision" : 5,
        "double_downs": 3,
        "amount": 0.1 
    },
    "BNBBTC": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "BNB",
        "currency": "BTC",
        "precision" : 7,
        "double_downs": 3,
        "amount": 0.1 
    },
    "ADABNB": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "ADA",
        "currency": "BNB",
        "precision" : 7,
        "double_downs": 3,
        "amount": 20 
    },
    "ADABTC": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "ADA",
        "currency": "BTC",
        "precision" : 7,
        "double_downs": 3,
        "amount": 20 
    },
    "MATICBNB": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "MATIC",
        "currency": "BNB",
        "precision" : 7,
        "double_downs": 3,
        "amount": 20 
    },
    "MATICBTC": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "MATIC",
        "currency": "BTC",
        "precision" : 7,
        "double_downs": 3,
        "amount": 20 
    },
    "ETHBTC": {
        "medium_period_to_compare": 6,
        "short_period_to_compare": 30,
        "crypto": "ETH",
        "currency": "BTC",
        "precision" : 7,
        "double_downs": 3,
        "amount": 0.015 
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