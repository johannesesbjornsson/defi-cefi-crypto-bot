
import cfg as cfg
import itertools
import sys
import arbitrage
sys.path.insert(0,'../libraries')
from eth_fork_client import Client, Token, TokenPair
import eth_fork_client
import token_config

client = eth_fork_client.Client("bsc",cfg.my_bep20_address, cfg.private_key, cfg.bsc_scan_api_key)

lists = list(itertools.combinations(client.tokens_to_check, 2))
lists = list(itertools.combinations(token_config.bep20_tokens_to_check, 2))
#lists = [
#    ["LINK", "DOT"]
#]


token_1 = Token(client, "BUSD")

from_range = [10,20]
for li in lists:
    print(li[0],li[1])
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
    