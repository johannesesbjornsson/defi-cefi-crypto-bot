import asyncio
import time
import sys
sys.path.insert(0,'../libraries')
from eth_fork_client import Client
from eth_fork_token import Token
from eth_fork_transaction import Transaction
from eth_fork_triggers import Triggers
import cfg as cfg


pending_transactions = [
"0xfd79b8b3186d0c52d59a87e77f292d460a13d121c34078cd5cc8d29cb8cb912c",
"0xfd79b8b3186d0c52d59a87e77f292d460a13d121c34078cd5cc8d29cb8cb912c",
"0xfd79b8b3186d0c52d59a87e77f292d460a13d121c34078cd5cc8d29cb8cb912c",
"0xfd79b8b3186d0c52d59a87e77f292d460a13d121c34078cd5cc8d29cb8cb912c",
"0xfd79b8b3186d0c52d59a87e77f292d460a13d121c34078cd5cc8d29cb8cb912c",
"0xfd79b8b3186d0c52d59a87e77f292d460a13d121c34078cd5cc8d29cb8cb912c",
"0xfd79b8b3186d0c52d59a87e77f292d460a13d121c34078cd5cc8d29cb8cb912c",
"0xfd79b8b3186d0c52d59a87e77f292d460a13d121c34078cd5cc8d29cb8cb912c",
"0xfd79b8b3186d0c52d59a87e77f292d460a13d121c34078cd5cc8d29cb8cb912c",
]

#async def fetch_single_transaction(transaction_hash):
#
#    #print(f"Printing {n}")
#    #await asyncio.sleep(1)
#    #f = n +"1"
#    try:
#        transaction_hash = client.web3.toHex(transaction_hash)
#    except TypeError as e:
#        transaction_hash = transaction_hash
#
#    print(transaction_hash)
#    transaction_info = await client.web3_asybc.eth.get_transaction(transaction_hash)
#    txn = Transaction(client, transaction_info)
#    return transaction_info
#
#async def fetch_transactions(n):
#    saved_txns = []
#    done, pending = await asyncio.wait(
#        [fetch_single_transaction(arg) for arg in n]
#    )
#    for d in done:
#        saved_txns.append(d.result())
#    return saved_txns
#
#async def test():
#    return 1
#
#async def test1():
#    return 1
#
#async def test2():
#    all_groups = asyncio.wait((await test(), await test1()))


if __name__ == "__main__":
    client = Client("polygon",cfg.my_polygon_address, cfg.private_key, cfg.polygon_api_key)
    triggers = Triggers(client)
    test = []
    while True:
        

        start = time.perf_counter()
        pending_router_transactions = asyncio.run(triggers.get_router_contract_interaction(pending_transactions))
        
        for txn in pending_router_transactions:
            triggers.handle_swap_transaction(txn)
        end = time.perf_counter()
        test.append(end - start)
        print("-----------------------")
        print("Time elapsed average: ", sum(test) / len(test))
        print("-----------------------")