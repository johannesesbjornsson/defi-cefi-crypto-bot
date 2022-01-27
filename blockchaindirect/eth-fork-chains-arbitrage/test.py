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
    client = Client("polygon",cfg.my_address, cfg.private_key,cfg.api_key)
    triggers = Triggers(client)
    test = []
    #test_req()
    while True:

        #token_1 = Token(client, "0x22ffbe8b309abe8bbc28bf08c8ed3d6734c80dcc")
        for token in test_t:
            token_1 = Token(client, token, "local")
        client.write_token_info_to_file()

        print("-----------------------")
        break
        time.sleep(2)