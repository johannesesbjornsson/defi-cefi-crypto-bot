import asyncio
import time
import sys
sys.path.insert(0,'../libraries')
from eth_fork_client import Client
from eth_fork_token import Token
from eth_fork_transaction import Transaction
import cfg as cfg
client = Client("polygon",cfg.my_polygon_address, cfg.private_key, cfg.polygon_api_key)

txns = [
"0x12b2b4a510348d96753b924a69c5f1eea38defa64d9c519a6bcfe92d838a8618",
]

async def fetch_single_transaction(transaction_hash):

    #print(f"Printing {n}")
    #await asyncio.sleep(1)
    #f = n +"1"
    try:
        transaction_hash = client.web3.toHex(transaction_hash)
    except TypeError as e:
        transaction_hash = transaction_hash

    print(transaction_hash)
    transaction_info = await client.web3_asybc.eth.get_transaction(transaction_hash)
    txn = Transaction(client, transaction_info)
    return transaction_info

async def fetch_transactions(n):
    saved_txns = []
    done, pending = await asyncio.wait(
        [fetch_single_transaction(arg) for arg in n]
    )
    for d in done:
        saved_txns.append(d.result())
    return saved_txns



if __name__ == "__main__":
    start = time.perf_counter()
    #saved_txns = asyncio.run(fetch_transactions(txns))
    #print(saved_txns)
    saved_txns = asyncio.run(fetch_single_transaction(txns[0]))
    end = time.perf_counter()
    print("Time elapsed",end - start)