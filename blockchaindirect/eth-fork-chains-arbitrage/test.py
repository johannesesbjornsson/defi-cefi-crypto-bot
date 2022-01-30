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
"0xb33d68afbbfb7979af47ed996d3e38b677d3f6b64d0f6877aed0d71df09033ca",
#"0x39a2380a9d7a796699b12eeb3ed030f53854a6be855dc9dc982336c8ad2888fa",
]

def run_some_tests(polygon_client):
    token_1 = Token(polygon_client, "USDC")
    token_2 = Token(polygon_client, "WMATIC")
    token_pair = TokenPair(polygon_client, token_1, token_2)
    token_pair.token_1_liquidity = 20000
    token_pair.token_2_liquidity = 10000
    txn_hash_1 = "0x4b28cc27f73fab2906a96b3380b0d53224b4f364c8e3bfd0d87008bf6ccb9d8c"
    transaction_info = polygon_client.web3.eth.get_transaction(txn_hash_1)
    txn = Transaction(polygon_client,transaction_info)
    router_txn = RouterTransaction(txn)
    amount_in = token_pair.token_1.to_wei(1000)


    router_txn.amount_in = amount_in
    router_txn.amount_out = token_pair.token_2.to_wei(456.76)
    
    liquidity_impact, txn_value = token_pair.quick_router_transction_analysis(router_txn)
    print(liquidity_impact,txn_value)

    amount_out = token_pair.get_amount_token_2_out(amount_in,offline_calculation=True)
    print(token_pair.token_2.from_wei(amount_out))

if __name__ == "__main__":
    #client = Client("polygon",cfg.my_polygon_address, cfg.private_key)
    client = Client("polygon",cfg.my_address, cfg.private_key,cfg.api_key)
    triggers = Triggers(client)
    test = []
    #test_req()
    while True:
        start = time.perf_counter()
        #token_1 = Token(client, "USDC", "local")
        #token_2 = Token(client, "WMATIC", "local")
        #end = time.perf_counter()
        
        #token_pair = TokenPair(client,token_1, token_2, "local")
        #transaction_info = client.web3.eth.get_transaction("0xb33d68afbbfb7979af47ed996d3e38b677d3f6b64d0f6877aed0d71df09033ca")
        #txn = Transaction(client, transaction_info)
        #r_txn = RouterTransaction(txn)
        #token_pair.quick_router_transction_analysis(r_txn)
        transaction_info = client.web3.eth.get_transaction("0x5205f391d9e139e5d33505512adc29ca9136329f661e0897b2d15a9464d0685b")
        print(transaction_info)
        print("---")
        transaction_info = client.web3.eth.get_transaction("0x81b7be2d290c0a26b8b5ede5350e3d123d32c6959e9983b9f4cc36e07cc40ace")
        print(transaction_info)
        end = time.perf_counter()
        
        print("Time elapsed", end-start)


        #txn_list = client.get_account_transaction("0x837107fa17efd21a10c5fc43fadfbe79bd29cc94")
        #account = Account(client,"0x837107fa17efd21a10c5fc43fadfbe79bd29cc94")
        #txn = account.get_next_router_txn(264)
        #print(txn)
        #transaction_info = client.web3.eth.get_transaction("0x0422e424de70ba273ae1deec4bccb2cde83495b2ed4f1dd8d010480ad0699721")
        #txn = Transaction(client, transaction_info)
        #triggers.watch_transactions([None, txn])

        
        print("-----------------------")
        break
        time.sleep(2)