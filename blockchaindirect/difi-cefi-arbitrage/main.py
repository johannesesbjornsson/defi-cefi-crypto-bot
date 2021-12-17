


import itertools
import sys
import arbitrage
sys.path.insert(0,'../libraries')
import pancakeswap_client
import cfg as cfg
import token_config

client = pancakeswap_client.Client(cfg.my_bep20_address, cfg.private_key, cfg.bsc_scan_api_key)

token_list = token_config.tokens_to_check
#lists = [
#    ["WBNB", "MiniDOGE"]
#]
debug_mode = False
from_range = [5, 20]
for token in token_list:
    token_0 = "BUSD"
    token_1 = token
    print("Checking",token_0, token_1 )
    
    