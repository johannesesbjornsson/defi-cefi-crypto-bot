import sys
sys.path.insert(0,'../libraries')
from pancakeswap_client import Client

from binance_client import BinanceClient

class Arbitrage(object):

    def __init__(self, binance_client, pancakeswap_client, token_0, token_1, from_range=[20,50], debug_mode=False):
        if type(pancakeswap_client) != Client:
            raise ValueError("Argument must be object type Client")
        if type(binance_client) != BinanceClient:
            raise ValueError("Argument must be object type BinanceClient")
        self.binance_client = binance_client
        self.pancakeswap_client = pancakeswap_client
        self.debug_mode = debug_mode
        self.token_0 = token_0
        self.token_1 = token_1
        self.from_range = from_range
        self.token_0_hash = self.pancakeswap_client.known_tokens[token_0]
        self.token_1_hash = self.pancakeswap_client.known_tokens[token_1]

    def find_arbitrage(self):
        initial_swap_amount = 20
        #print("Amount out binance: ", self.binance_client.get_token_amount_out(self.token_0, self.token_1,from_token_amount))
        #amount_out = self.pancakeswap_client.get_token_amount_out(self.token_0,self.token_1,self.pancakeswap_client.web3.toWei(from_token_amount,'ether'))
        #print("Amount out pancakeswap: ", self.pancakeswap_client.web3.fromWei(amount_out,'ether'))

        # Buy from pancakeswap and sell binance
        amount_out_wei = self.pancakeswap_client.get_token_amount_out(self.token_0,self.token_1,self.pancakeswap_client.web3.toWei(initial_swap_amount,'ether'))
        if amount_out_wei is not None:
            amount_out_pancakeswap =  self.pancakeswap_client.web3.fromWei(amount_out_wei,'ether')
            amount_out_binance = self.binance_client.get_token_amount_out(self.token_1, self.token_0, float(amount_out_pancakeswap))
            if amount_out_binance > initial_swap_amount:
                print("Pancakeswap buy -> Binance sell")
                print("Tokens out from binance: ",amount_out_binance)
                print("Profit", amount_out_binance - initial_swap_amount)
        
        
        # Buy from binance and sell at pancakeswap
        amount_out_binance = self.binance_client.get_token_amount_out(self.token_0, self.token_1, float(initial_swap_amount))
        amount_out_wei = self.pancakeswap_client.get_token_amount_out(self.token_1,self.token_0,self.pancakeswap_client.web3.toWei(amount_out_binance,'ether'))

        
        if amount_out_wei is not None:
            amount_out_pancakeswap =  self.pancakeswap_client.web3.fromWei(amount_out_wei,'ether')
            if amount_out_pancakeswap > initial_swap_amount:
                print("Binance buy -> Pancakeswap sell")
                print("Tokens out from binance: ", amount_out_pancakeswap)
                print("Profit", amount_out_pancakeswap - initial_swap_amount)

        





    
    