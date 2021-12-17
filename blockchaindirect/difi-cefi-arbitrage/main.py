
import cfg as cfg
import itertools
import sys
import arbitrage
sys.path.insert(0,'../libraries')
import pancakeswap_client
import token_config
from binance_client import BinanceClient

client = pancakeswap_client.Client(cfg.my_bep20_address, cfg.private_key, cfg.bsc_scan_api_key)
binance_client = BinanceClient(cfg.api_key,cfg.api_secret,cfg.my_bep20_address)
token_list = token_config.tokens_to_check
#lists = [
#    ["WBNB", "MiniDOGE"]
#]
debug_mode = False
from_range = [5, 20]
for token in token_list:
    token_0 = "BUSD"
    token_1 = token

    print(binance_client.get_price(token_1,token_0))
    
    