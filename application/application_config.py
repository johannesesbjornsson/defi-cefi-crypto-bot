import os

assets_to_check = {
    "BTC": {
        "precision" : 6,
        "gbp_amount" : 50
    },
    "ETH": {
        "precision" : 4,
        "gbp_amount" : 50
    },
    "BNB": {
        "precision" : 4,
        "gbp_amount" : 50
    },   
}

cryptopairs = {
    "BNBETH": {
        "crypto": "BNB",
        "currency": "ETH",
        "precision" : 5,
        "amount": 0.05 
    },
    "BNBBTC": {
        "crypto": "BNB",
        "currency": "BTC",
        "precision" : 7,
        "amount": 0.005 
    },
    #"ETHBTC": {
    #    "precision" : 4,
    #    "gbp_amount" : 50
    #},   
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