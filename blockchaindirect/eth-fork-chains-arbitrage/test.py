import asyncio
import time
import sys
sys.path.insert(0,'../libraries')
from eth_fork_client import Client
from eth_fork_token import Token
from eth_fork_transaction import Transaction, RouterTransaction
from eth_fork_triggers import Triggers
from eth_fork_token_pair import TokenPair
import cfg as cfg


pending_transactions = [
"0x5fd2b41e32392662a61af5cd0518311760fc71937784b4159ebaef1ce4a19881",
#"0x39a2380a9d7a796699b12eeb3ed030f53854a6be855dc9dc982336c8ad2888fa",
]


#async def test():
#    return 1
#
#async def test1():
#    return 1
#
#async def test2():
#    all_groups = asyncio.wait((await test(), await test1()))

def test_req():
    import requests
    import json
    from eth_abi import decode_abi
    from eth_utils import to_bytes

    #params = liquidity_pool_contract.encodeABI(fn_name="token1",args=[])
    data = {"jsonrpc": "2.0", "method": "eth_call", "params": [{"to": "0x2cF7252e74036d1Da831d11089D326296e64a728", "data": "0xd21220a7"}, "latest"], "id": 1}
    response = requests.post("https://polygon-rpc.com", headers={"Content-Type":"application/json"},json=data)
    hex_str = response.json()["result"]
    decoded = decode_abi(['address'], to_bytes(hexstr=hex_str))
    print(decoded)
    

if __name__ == "__main__":
    #client = Client("polygon",cfg.my_polygon_address, cfg.private_key)
    client = Client("polygon",cfg.my_address, cfg.private_key)
    triggers = Triggers(client)
    test = []
    #test_req()
    while True:
        start = time.perf_counter()
        #token_1 = Token(client, "WFTM")
        #token_2 = Token(client, "ETH")
        
        token_1 = Token(client, "WMATIC")
        end = time.perf_counter()
        print(end - start)

        start = time.perf_counter()
        token_2 = Token(client, "USDC", "local")
        end = time.perf_counter()
        print(end - start)

        start = time.perf_counter()
        token_pair = TokenPair(client, token_1, token_2)
        end = time.perf_counter()
        print(end - start)           
        

        #asyncio.run(self.watch_competing_transaction(router_txn.transaction))
        #start = time.perf_counter()
        #pending_router_transactions = asyncio.run(triggers.get_router_contract_interaction(pending_transactions))
        #for txn in pending_router_transactions:
        #    print (txn[0].input_data)
        #    print (txn[2])
        
        
        #end = time.perf_counter()
        #test.append(end - start)
        #print("-----------------------")
        #print("Time elapsed average: ", sum(test) / len(test))
        print("-----------------------")
        break
        time.sleep(2)