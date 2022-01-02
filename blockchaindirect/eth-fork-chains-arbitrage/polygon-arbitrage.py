
import cfg as cfg
import itertools
import sys
import arbitrage
sys.path.insert(0,'../libraries')
from eth_fork_client import Client
from eth_fork_token import Token
from eth_fork_token_pair import TokenPair
from eth_fork_triggers import Triggers
import token_config

from web3 import Web3

client = Client("polygon",cfg.my_polygon_address, cfg.private_key, cfg.polygon_api_key)

lists = list(itertools.combinations(client.tokens_to_check, 2))
lists = [
    #["WETH", "WMATIC"],
    #["QUICK", "LINK"]
]
token_1 = Token(client, "USDC")

triggers = Triggers(client)
triggers.get_pending_transactions()

from_range = [0.1,0.1]
for li in lists:
    token_2 = Token(client, li[0])
    token_3 = Token(client, li[1])
    token_pair_1 = TokenPair(client, token_1, token_2)
    token_pair_2 = TokenPair(client, token_2, token_3)
    token_pair_3 = TokenPair(client, token_1, token_3)


    
    print("Checking: ",token_1.name, token_2.name, token_3.name )
    arbitrage_client = arbitrage.Arbitrage(client=client,
        token_pair_1=token_pair_1, 
        token_pair_2=token_pair_2, 
        token_pair_3=token_pair_3,
        from_range=from_range)

    found_arbitrage =  arbitrage_client.find_arbitrage()
    if found_arbitrage:
        #arbitrage_client.execute_arbitrage()
        print("------------------------")