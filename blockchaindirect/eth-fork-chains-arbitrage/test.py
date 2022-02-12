import asyncio
import time
import sys
import json
import logic
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


def test(client):
    token_1 = Token(client, "WMATIC", "local")
    #token_2 = Token(client, "USDC")
    token_2 = Token(client, "USDC")
    token_pair = TokenPair(client,token_1, token_2)
    amount_in = token_pair.token_1.to_wei(1)
    amount_out = token_pair.get_amount_token_2_out(amount_in,offline_calculation=True)
    token_pair.swap_token_1_for_token_2(amount_in,amount_out,38576412146,1)



if __name__ == "__main__":
    #client = Client("polygon",cfg.my_polygon_address, cfg.private_key)
    client = Client("polygon",cfg.my_address, cfg.private_key,cfg.api_key)
    triggers = Triggers(client, "local")
    #test_req()
    print("------- START ----------")
    while True:
        start = time.perf_counter() 
        #re_init_tokens(client)
        #test(client)
        #test_txn_analysis(client)
        write_contract_code_to_file(client, "0x08e175a1eac9744a0f1ccaeb8f669af6a2bda3ce")



        #transaction_info = client.web3.eth.get_transaction("0x29e3beec594d6ed92bec7975f4b576111d90de69566d4e9b1afa56bac761019f")
        #txn = Transaction(client, transaction_info)
        #r_txn = RouterTransaction(txn)
        #triggers.watch_transactions(r_txn.transaction, False)
        print("---")

        #token_1 = Token(client, "0x08e175a1eac9744a0f1ccaeb8f669af6a2bda3ce")
        #print(token_1.safe_code)

        #transaction_info = client.web3.eth.get_transaction("0x81b7be2d290c0a26b8b5ede5350e3d123d32c6959e9983b9f4cc36e07cc40ace")
        #print(transaction_info)
        #maxPriorityFeePerGas = client.web3.eth.max_priority_fee
        #print(client.web3.fromWei(maxPriorityFeePerGas,'gwei'))
        #maxFeePerGas = client.web3.eth.max_priority_fee + (2 * client.web3.eth.get_block('latest')['baseFeePerGas'])
        #print(client.web3.fromWei(maxFeePerGas,'gwei'))
        #end = time.perf_counter()
        
        #print("Time elapsed", end-start)

#33768815600 gasPrice
#33777116648 maxFeePerGas
#33758912335 maxPriorityFeePerGas


        
        print("-----------------------")
        break
        time.sleep(2)