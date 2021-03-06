import asyncio
import time
import sys
import logging
import json
import logic
sys.path.insert(0,'../libraries')
from blockchain_client import Client
from tokens import Token
from transaction import Transaction, RouterTransaction
from triggers import Triggers
from token_pair import TokenPair
from account import Account
from transaction_scanner import TransactionScanner
import cfg as cfg


pending_transactions = [
"0xb33d68afbbfb7979af47ed996d3e38b677d3f6b64d0f6877aed0d71df09033ca",
#"0x39a2380a9d7a796699b12eeb3ed030f53854a6be855dc9dc982336c8ad2888fa",
]

def re_init_tokens(client):
    with open('../libraries/settings/polygon/tokens_backup.json', 'r') as f: 
    	data = json.load(f)
    for token_hash in data:
        token = Token(client, token_hash, "local")
        if token.safe_code == False and token.verified == True:
            print("------------------------")
            print("------ HAS FEES --------")
            print("------------------------")
            print(token)
            print(token.safe_code)
            print("------------------------")
    client.write_token_info_to_file() 

def re_init_token_pairs(client):
    with open('../libraries/settings/polygon/pairs_backup.json', 'r') as f: 
    	data = json.load(f)
    for pair in data:

        pairs = pair.split("_")
        start = time.perf_counter()
        token_1 = Token(client, pairs[0], "local")
        token_2 = Token(client, pairs[1], "local")
        token_pair = TokenPair(client,token_1, token_2,"local")
        end = time.perf_counter()
        print(end-start)
        if token_pair.has_token_fees:
            print("------------------------")
            print("------ HAS FEES --------")
            print("------------------------")
            print(token_pair)
            print(token_pair.has_token_fees)
            print("------------------------")


def write_contract_code_to_file(client, address):
        response_code, response_json = client.get_abi(address)
        token = Token(client, address)
        if response_code == 200:
            if "SourceCode" in response_json["result"][0]:
                with open(token.symbol+".sol", 'w') as f:
                    f.write(response_json["result"][0]["SourceCode"])

def test_txn_analysis(polygon_client):
    token_1 = Token(client, "WMATIC", "local")
    token_2 = Token(client, "0xc17b109e146934d36c33e55fade9cbda791b0366")
    token_pair = TokenPair(client,token_1, token_2)
    txn_hash_1 = "0x6f47f9bdf30c54e21ebe7b057570e97608116d4430e9c85ffdd811faa5253b98"
    transaction_info = polygon_client.web3.eth.get_transaction(txn_hash_1)
    txn = Transaction(polygon_client,transaction_info)
    router_txn = RouterTransaction(txn)
    liquidity_impact, txn_value, slippage, attacking_txn_max_amount_in = token_pair.quick_router_transction_analysis(router_txn)


async def test_handle_swap_txn(polygon_client, triggers):
    if triggers.init_type != "live":
        print(wrong)
    txn_hash = "0xc40c4206fea214137434ee429ee8959301c0f25983271e56eb4cbd002966315a"
    transaction_info = await polygon_client.web3_asybc.eth.get_transaction(txn_hash)
    txn = Transaction(polygon_client, transaction_info)
    router_txn = RouterTransaction(txn)
    triggers.handle_swap_transaction(router_txn)

async def trigger_handle_swp(polygon_client, triggers):
    done, pending = await asyncio.wait(
            [test_handle_swap_txn(polygon_client, triggers) for number in range(100)]
        )
    for result in done:
        res = result.result()

def test(client):
    token_1 = Token(client, "WMATIC", "local")
    #token_2 = Token(client, "USDC")
    token_2 = Token(client, "USDC")
    token_pair = TokenPair(client,token_1, token_2)
    amount_in = token_pair.token_1.to_wei(1)
    amount_out = token_pair.get_amount_token_2_out(amount_in,offline_calculation=True)
    #client.async_contract_function_call(token_pair.liquidity_pool_address, token_pair.liquidity_pool_contract)
    #token_pair.swap_token_1_for_token_2(amount_in,amount_out,38576412146,1)

if __name__ == "__main__":
    logger = logging.getLogger("unittests")
    logger.setLevel(logging.INFO)
    client = Client("polygon", cfg.my_address, cfg.private_key, cfg.node_key, logger, cfg.api_key)
    #txn_scanner = TransactionScanner(client)
    #triggers = Triggers(client, "local")
    triggers = Triggers(client, "live")
    print("------- START ----------")
    while True:
        #start = time.perf_counter() 
        #re_init_tokens(client)
        test(client)
        #test_txn_analysis(client)
        #write_contract_code_to_file(client, "0x08e175a1eac9744a0f1ccaeb8f669af6a2bda3ce")
        
        #asyncio.run(trigger_handle_swp(client, triggers))
        
        print("-----")
