import asyncio
import time
import sys
sys.path.insert(0,'../libraries')
from eth_fork_client import Client
from eth_fork_token import Token
from eth_fork_transaction import Transaction, RouterTransaction
from eth_fork_triggers import Triggers
from eth_fork_token_pair import TokenPair
from eth_fork_account import Account
import cfg as cfg


pending_transactions = [
"0x5fd2b41e32392662a61af5cd0518311760fc71937784b4159ebaef1ce4a19881",
#"0x39a2380a9d7a796699b12eeb3ed030f53854a6be855dc9dc982336c8ad2888fa",
]

if __name__ == "__main__":
    #client = Client("polygon",cfg.my_polygon_address, cfg.private_key)
    client = Client("polygon",cfg.my_address, cfg.private_key,cfg.api_key)
    triggers = Triggers(client)
    test = []
    #test_req()
    while True:

        #token_1 = Token(client, "0x22ffbe8b309abe8bbc28bf08c8ed3d6734c80dcc")

        #txn_list = client.get_account_transaction("0x837107fa17efd21a10c5fc43fadfbe79bd29cc94")
        #account = Account(client,"0x837107fa17efd21a10c5fc43fadfbe79bd29cc94")
        #txn = account.get_next_router_txn(264)
        #print(txn)
        transaction_info = client.web3.eth.get_transaction("0x0422e424de70ba273ae1deec4bccb2cde83495b2ed4f1dd8d010480ad0699721")
        txn = Transaction(client, transaction_info)
        triggers.watch_transactions([None, txn])

        
        print("-----------------------")
        break
        time.sleep(2)