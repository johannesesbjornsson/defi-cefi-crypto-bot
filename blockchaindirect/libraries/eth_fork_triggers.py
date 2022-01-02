import contract_libarary
import time
import token_config
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError, TransactionNotFound
from web3.middleware import geth_poa_middleware
from eth_fork_token import Token

class Triggers(object):

    def __init__(self, client):
        self.client = client

    def handle_swap_transaction(self,gas_price, txn_input):
        print(gas_price)
        #token_1 = Token()
        print(txn_input)

    def get_pending_transactions(self):
        self.client.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        pending = self.client.web3.eth.get_block(block_identifier='pending', full_transactions=True)
        #pending = self.client.web3.eth.filter('pending').get_all_entries()
        
        #print(pending)
        i = 1
        for entry in pending["transactions"]:
            if entry["to"] == self.client.router_contract_address:
                txn_input = self.client.router_contract.decode_function_input(entry["input"])
                gas_price = entry["gasPrice"]
                txn_hash = self.client.web3.toHex(entry["hash"])
                function_called = txn_input[0]
                input_data = txn_input[1]

                
                print(txn_hash)
                if "Function swap" in str(function_called):
                    self.handle_swap_transaction(gas_price, input_data)
                

                transaction_receipt, transaction_successful, transaction_complete = self.client.get_transaction_receipt(txn_hash=txn_hash, wait=False)
                if transaction_complete:
                    print("Too slow....")
                else:
                    print("Winning!!")
                
                
                start = time.perf_counter()
                transaction_receipt, transaction_successful, transaction_complete = self.client.get_transaction_receipt(txn_hash=txn_hash, wait=True)
                print(transaction_successful)
                end = time.perf_counter()
                print(end - start)
                print("--------")
                