from binance.client import Client
from binance.exceptions import BinanceAPIException


class BinanceClient(object):

    def __init__(self, api_key,api_secret, my_bep20_address):
        self.client = Client(api_key, api_secret)
        self.my_address = my_bep20_address

    def get_price(self,token_0,token_1):
        try:
            price = self.client.get_symbol_ticker(symbol=token_0+token_1).get("price")
        except BinanceAPIException as e:
            price = None
        
        return price