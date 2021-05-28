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
    "XRP": {
        "precision" : 1,
        "gbp_amount" : 50
    },
}

#api_key = os.environ.get('binance_api')
#api_secret = os.environ.get('binance_secret')
#email_api_key = os.environ.get('email_api_key')
api_key = os.environ['binance_api']
api_secret = os.environ['binance_secret']
email_api_key = os.environ['email_api_key']