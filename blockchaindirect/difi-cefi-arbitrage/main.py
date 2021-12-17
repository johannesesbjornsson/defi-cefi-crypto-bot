


import itertools
import sys
import arbitrage
sys.path.insert(0,'../libraries')
import pancakeswap_client
import cfg as cfg

client = pancakeswap_client.Client(cfg.my_bep20_address, cfg.private_key, cfg.bsc_scan_api_key)

lists = cfg.tokens_to_check
#lists = [
#    ["WBNB", "MiniDOGE"]
#]
debug_mode = False
from_range = [5, 20]
for token in lists:
    token_0 = "BUSD"
    token_1 = token
    print("Checking",token_0, token_1 )
    
    arbitrage_client = arbitrage.Arbitrage(client=client,token_0=token_0,token_1=token_1,token_2=token_2,from_range=from_range, debug_mode=debug_mode)
    #client.approve_token("BabyDoge")
    #client.estimate_gas_price()
    
    found_arbitrage =  arbitrage_client.find_arbitrage()
    