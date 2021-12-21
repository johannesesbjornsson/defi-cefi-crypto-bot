
import cfg as cfg
import itertools
import sys
import arbitrage
sys.path.insert(0,'../libraries')
import eth_fork_client
import token_config

client = eth_fork_client.Client("bsc",cfg.my_bep20_address, cfg.private_key, cfg.bsc_scan_api_key)

lists = list(itertools.combinations(client.tokens_to_check, 2))
lists = list(itertools.combinations(token_config.bep20_tokens_to_check, 2))
#lists = [
#    ["WBNB", "ADA"]
#]


debug_mode = False
from_range = [1, 2]

for li in lists:
    token_0 = "BUSD"
    token_1 = li[0]
    token_2 = li[1]
    print("Checking: ",token_0, token_1, token_2 )
    
    arbitrage_client = arbitrage.Arbitrage(client=client,token_0=token_0,token_1=token_1,token_2=token_2,from_range=from_range, debug_mode=debug_mode)

    found_arbitrage =  arbitrage_client.find_arbitrage()
    if found_arbitrage:
        print(found_arbitrage)
        #arbitrage_client.execute_arbitrage()
        print("------------------------")
    