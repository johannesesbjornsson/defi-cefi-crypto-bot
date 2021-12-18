
import cfg as cfg
import itertools
import sys
import arbitrage
sys.path.insert(0,'../libraries')
from eth_fork_client import Client
import token_config

from web3 import Web3

client = Client("polygon",cfg.my_polygon_address, cfg.private_key, cfg.api_key)

lists = list(itertools.combinations(client.tokens_to_check, 2))
lists = [
    #["WETH", "WMATIC"],
    ["WBTC", "LINK"]
]

debug_mode = False
from_range = [2,3]
for li in lists:
    token_0 = "USDC"
    #token_0 = "WMATIC"
    token_1 = li[0]
    token_2 = li[1]
    print("Checking: ",token_0, token_1, token_2 )
    arbitrage_client = arbitrage.Arbitrage(client=client,token_0=token_0,token_1=token_1,token_2=token_2,from_range=from_range, debug_mode=debug_mode)

    found_arbitrage =  arbitrage_client.find_arbitrage()
    if found_arbitrage:
        arbitrage_client.execute_arbitrage()
    #client.approve_token("LINK")
    #print(found_arbitrage)
    #print(client.get_token_amount_out(token_0, token_1,1000000000000000000))
    
    #print(token_0,token_1)
    #print(client.web3.fromWei(client.get_token_amount_out(token_0, token_1,1000000000000000000),'ether'))
    #print(client.get_amount_out_by_liqudity_pool(token_0, token_1,1000000000000000000))
    
    print("--------------------------------")
    #
    #t0_l, t1_l, addr = arbitrage_client.client.get_pair_liquidity(token_0,token_1)
    #print(token_0, token_1, "||LIQ:",t0_l, t1_l,addr)
    #print(float(t0_l) * 1000000000000)
    #client.web3.fromWei(initial_swap_amount,'ether')