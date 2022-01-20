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
"0xfd79b8b3186d0c52d59a87e77f292d460a13d121c34078cd5cc8d29cb8cb912c",
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
    client = Client("bsc",cfg.my_polygon_address, cfg.private_key)
    triggers = Triggers(client)
    test = []
    #test_req()
    while True:
        


        #token_1 = Token(client, "WBNB")
        #token_2 = Token(client, "BUSD")
        #start = time.perf_counter()
        #token_pair_1 = TokenPair(client, token_1, token_2)
        #transaction_info = client.web3.eth.get_transaction("0xdb72da926b63793996df7cf48b7a58d9656afd3666defcf92a6068dab78d8c5a")
        #txn = Transaction(client,transaction_info)
        #router_txn = RouterTransaction(txn)
        break

        
        #pending_router_transactions = asyncio.run(triggers.get_router_contract_interaction(pending_transactions))
        #for txn in pending_router_transactions:
        #    triggers.handle_swap_transaction(txn)
        #end = time.perf_counter()
        #test.append(end - start)
        #print("-----------------------")
        #print("Time elapsed average: ", sum(test) / len(test))
        #print("-----------------------")
        ##break
        #time.sleep(2)