from binance.client import Client
from binance.exceptions import BinanceAPIException


class BinanceClient(object):

    def __init__(self, api_key,api_secret, my_bep20_address):
        self.client = Client(api_key, api_secret)
        self.my_address = my_bep20_address

    def get_price(self, token_0, token_1):
        try:
            symbol =  token_0 + token_1
            price = self.client.get_symbol_ticker(symbol=symbol).get("price")
            price = float(price)
        except BinanceAPIException as e:
            price = None
        
        return price

    def get_token_amount_out(self, from_token, to_token, from_token_amount):
        amount_out_per_token = 0
        price = self.get_price(from_token,to_token)
        if price is None:
            price = self.get_price(to_token,from_token)
            if price is not None:
                amount_out_per_token = 1/price

        else:
            amount_out_per_token = price

        amount_out = amount_out_per_token * from_token_amount

        return amount_out