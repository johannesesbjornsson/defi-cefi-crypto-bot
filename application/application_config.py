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
    #"XRP": {
    #    "precision" : 1,
    #    "gbp_amount" : 50
    #},
    #"ADA": {
    #    "precision" : 1,
    #    "gbp_amount" : 50
    #},    
}

precision_dict = {
    "BTC": {
        "precision" : 6,
        "price_precision": 0.01
    },
    "ETH": {
        "precision" : 4,
        "price_precision": 0.01
    },
    "BNB": {
        "precision" : 4,
        "price_precision": 0.01
    },
    "XRP": {
        "precision" : 1,
        "price_precision": 0.000001
    },
    "ADA": {
        "precision" : 1,
        "price_precision": 0.000001
    },    
    "MATIC": {
        "precision" : 1,
        "price_precision": 0.000001
    }, 
}

#api_key = os.environ.get('binance_api')
#api_secret = os.environ.get('binance_secret')
#email_api_key = os.environ.get('email_api_key')
api_key = os.environ['binance_api']
api_secret = os.environ['binance_secret']
email_api_key = os.environ['email_api_key']