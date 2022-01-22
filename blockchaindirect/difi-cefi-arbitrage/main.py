
import cfg as cfg
import itertools
import sys
import arbitrage
sys.path.insert(0,'../libraries')
from pancakeswap_client import Client

from binance_client import BinanceClient

pancakeswap_client = Client(cfg.my_bep20_address, cfg.private_key, cfg.bsc_scan_api_key)
binance_client = BinanceClient(cfg.api_key,cfg.api_secret,cfg.my_bep20_address)
token_list = token_config.tokens_to_check

#token_list = ["DOGE", "XRP"]


debug_mode = False
from_range = [5, 20]
for token in token_list:
    token_0 = "BUSD"
    token_1 = token
    print("---------------------------")
    print("Checking: ", token_0, token_1)

    arbitrage_client = arbitrage.Arbitrage(binance_client=binance_client, pancakeswap_client=pancakeswap_client,token_0=token_0,token_1=token_1,from_range=from_range, debug_mode=debug_mode)

    arbitrage_client.find_arbitrage()
    
    
