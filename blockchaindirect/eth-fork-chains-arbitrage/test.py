import asyncio
import time
import sys
import json
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
    with open('../libraries/settings/polygon/token_backup.json', 'r') as f: 
    	data = json.load(f)
    for token_hash in data:
        print("-------")
        token = Token(client, token_hash, "local")
        print(token.safe_code)
    
    client.write_token_info_to_file() 

if __name__ == "__main__":
    #client = Client("polygon",cfg.my_polygon_address, cfg.private_key)
    client = Client("polygon",cfg.my_address, cfg.private_key,cfg.api_key)
    triggers = Triggers(client)
    test = []
    #test_req()
    while True:
        start = time.perf_counter()
        re_init_tokens(client)
        #token_1 = Token(client, "WMATIC", "local")
        #token_2 = Token(client, "USDC", "local")
        #token_2 = Token(client, "0xCecAc06eeDe5E652D8215Ea369444919F43f5eD6")
        #end = time.perf_counter()
        #token_pair = TokenPair(client,token_1, token_2)

        #amount_in = token_pair.token_1.to_wei(1)
        #amount_out = token_pair.get_amount_token_2_out(amount_in,offline_calculation=True)
        #token_pair.swap_token_1_for_token_2(amount_in,amount_out,current_nonce)


        #transaction_info = client.web3.eth.get_transaction("0xe304b6628456990edd4650cb01e8611784a32dc59643af193af97fa28860d2c3")
        #txn = Transaction(client, transaction_info)
        #r_txn = RouterTransaction(txn)
        #triggers.watch_transactions([r_txn.transaction ])
        print("---")

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