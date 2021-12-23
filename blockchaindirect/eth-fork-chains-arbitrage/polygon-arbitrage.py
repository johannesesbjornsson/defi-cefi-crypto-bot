
import cfg as cfg
import itertools
import sys
import arbitrage
sys.path.insert(0,'../libraries')
from eth_fork_client import Client, Token, TokenPair
import token_config

from web3 import Web3

client = Client("polygon",cfg.my_polygon_address, cfg.private_key, cfg.polygon_api_key)

lists = list(itertools.combinations(client.tokens_to_check, 2))
lists = [
    #["WETH", "WMATIC"],
    #["WETH","LINK"]
]

token1 = Token(client, "USDC")
token2 = Token(client, "TEL")

token_pair = TokenPair(client, token1, token2)
print(token_pair)
print(token_pair.liquidity_pool_address)

#ina = 15.74
#out = token_pair.get_amount_token_1_out(ina)
#print(ina, out)
#print(token_pair.swap_token_2_for_token_1(ina,out))

debug_mode = False
from_range = [1,1]
for li in lists:
    token_0 = "USDC"
    #token_0 = "WMATIC"
    token_1 = li[0]
    token_2 = li[1]
    print("Checking: ",token_0, token_1, token_2 )
    arbitrage_client = arbitrage.Arbitrage(client=client,token_0=token_0,token_1=token_1,token_2=token_2,from_range=from_range, debug_mode=debug_mode)

    found_arbitrage =  arbitrage_client.find_arbitrage()
    if found_arbitrage:
        print(found_arbitrage)
        #arbitrage_client.execute_arbitrage()
        print("------------------------")
    
    #client.get_recent_transaction()
    
    #l0, l1, addr = client.get_pair_liquidity("TEL","USDC")
    #print(client.fromWei("TEL",l0))
    #print(client.fromWei("USDC",l1))
    
    #print(client.get_token_amount_out(token_0, token_1,1000000000000000000))
    
    #print(token_0,token_1)
    #print(client.get_amount_out_by_liqudity_pool(token_0, token_1,1000000))