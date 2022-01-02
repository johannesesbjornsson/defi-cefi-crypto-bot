import contract_libarary
import time
import token_config
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError, TransactionNotFound
from web3.middleware import geth_poa_middleware
from eth_fork_token import Token
from eth_fork_token_pair import TokenPair

class Triggers(object):

    def __init__(self, client):
        self.client = client
        if self.client.blockchain == "polygon":
            self.token_to_scan_for = self.client.web3.toChecksumAddress("0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270")
        elif self.client.blockchain == "bsc":
            self.token_to_scan_for =  self.client.web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")

        self.token_1 = Token(self.client,self.token_to_scan_for)

    def handle_swap_transaction(self,gas_price, txn_input):
        front_runnable = None
        
        try:
            input_token, out_token = txn_input["path"]
            if out_token == self.token_to_scan_for:
                token_2 = Token(self.client,input_token)
                front_runnable = True
                token_pair = TokenPair(self.client, self.token_1, token_2)
            else:
                token_pair = None
                

        except ValueError as e:
            token_pair = None
        
        
        if front_runnable:
            print(gas_price)
            print(txn_input)
            if "amountOut" in txn_input:
                txn_amount = self.token_1.from_wei(txn_input["amountOut"])
            elif "amountOutMin" in txn_input:
                txn_amount = self.token_1.from_wei(txn_input["amountOutMin"])
            print("Transaction value:",txn_amount)
            if txn_amount > 200:
                amount_in = self.token_1.to_wei(1)
                token_pair.get_amount_token_2_out(amount_in)
                
            
        

        return 

    def get_pending_transactions(self):
        self.client.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        pending = self.client.web3.eth.get_block(block_identifier='pending', full_transactions=True)
        #test = self.client.web3.eth.filter('pending').get_all_entries()
        
        #print(pending)

        for entry in pending["transactions"]:
            if entry["to"] == self.client.router_contract_address:
            
                txn_input = self.client.router_contract.decode_function_input(entry["input"])
                gas_price = entry["gasPrice"]
                txn_hash = self.client.web3.toHex(entry["hash"])
                function_called = txn_input[0]
                input_data = txn_input[1]

                
                
                if "Function swap" not in str(function_called):
                    continue

                print(txn_hash)
                self.handle_swap_transaction(gas_price, input_data)

                transaction_receipt, transaction_successful, transaction_complete = self.client.get_transaction_receipt(txn_hash=txn_hash, wait=False)
                if transaction_complete:
                    print("Too slow....")
                else:    
                    print("Winning!!")
                    #start = time.perf_counter()
                    #transaction_receipt, transaction_successful, transaction_complete = self.client.get_transaction_receipt(txn_hash=txn_hash, wait=True)
                    #print("Transaction successful: ",transaction_successful)
                    #end = time.perf_counter()
                    #print(end - start)
                
                
 
                print("--------")
                