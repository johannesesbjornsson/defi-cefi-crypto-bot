import contract_libarary
import time
import token_config
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError, TransactionNotFound, TimeExhausted
from web3.middleware import geth_poa_middleware
from eth_fork_token import Token, Transaction, RouterTransaction
from eth_fork_token_pair import TokenPair


class Triggers(object):

    def __init__(self, client):
        self.client = client
        if self.client.blockchain == "polygon":
            self.token_to_scan_for = self.client.web3.toChecksumAddress("0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270")
            self.scan_token_value = 0.1
            self.minimum_scanned_transaction = 5
        elif self.client.blockchain == "bsc":
            self.token_to_scan_for =  self.client.web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")
            self.minimum_scanned_transaction = 1
            self.scan_token_value = 0.005
        elif self.client.blockchain == "velas":
            self.token_to_scan_for =  self.client.web3.toChecksumAddress("0xc579D1f3CF86749E05CD06f7ADe17856c2CE3126")
            self.minimum_scanned_transaction = 1
            self.scan_token_value = 0.05

        self.token_1 = Token(self.client,self.token_to_scan_for)
        self.client.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    def handle_swap_transaction(self,gas_price, txn_input):
        token_pair = None
        amount_in = None
        amount_out = None
        try:
            input_token, out_token = txn_input["path"][-2:]
            if out_token == self.token_to_scan_for:
                token_2 = Token(self.client,input_token)
                token_pair = TokenPair(self.client, self.token_1, token_2)
            else:
                token_pair = None
        except ValueError as e:
            token_pair = None
        
        
        if token_pair:
            if "amountOut" in txn_input:
                txn_amount = self.token_1.from_wei(txn_input["amountOut"])
            elif "amountOutMin" in txn_input:
                txn_amount = self.token_1.from_wei(txn_input["amountOutMin"])

            if txn_amount > self.minimum_scanned_transaction:
                print("Transaction value:",txn_amount)
                amount_in = self.token_1.to_wei(self.scan_token_value)
                amount_out = token_pair.get_amount_token_2_out(amount_in)
                gas_price = gas_price + self.client.web3.toWei('1','gwei')

        return token_pair, amount_in, amount_out, gas_price

    def get_pending_transactions(self):
        tx_filter = self.client.web3_ws.eth.filter('pending')
        print("Taking a wee break")
        time.sleep(2)
        pending_transactions = tx_filter.get_new_entries()

        for transaction in pending_transactions:
            txn_hash = self.client.web3.toHex(transaction)
            try:
                transaction_info = self.client.web3.eth.get_transaction(txn_hash)
            except TransactionNotFound as e:
                continue

            txn = Transaction(self.client, transaction_info)


            if txn.to == self.client.router_contract_address and txn.block_number is None :

                router_txn = RouterTransaction(txn)
                
                if not router_txn.function_called.startswith("swap"):
                    continue

                token_pair, amount_in, amount_out, gas_price = self.handle_swap_transaction(router_txn.transaction.gas_price, router_txn.input_data)

                if not token_pair or not amount_in or not amount_out or not gas_price:
                    continue
                
                
                transaction_complete = router_txn.transaction.get_transaction_receipt(wait=False)
                
                if transaction_complete:
                    print("Too slow....")
                    print("Transaction successful: ",router_txn.transaction.successful)
                else:    
                    print("Winning!!")
                    print(router_txn.transaction.hash)
#                    amount_out_from_token_2 = token_pair.swap_token_1_for_token_2(amount_in, amount_out, gas_price)
#                    token_pair.token_2.approve_token()
#
#                    try:
#                        transaction_complete = router_txn.transaction.get_transaction_receipt(wait=True)
#                    except TimeExhausted as e:
#                        pass
#
#                    amount_out_from_token_1 = token_pair.get_amount_token_1_out(amount_out_from_token_2)
#                    token_pair.swap_token_2_for_token_1(amount_out_from_token_2, amount_out_from_token_1)
                    
                    #start = time.perf_counter()
                    #end = time.perf_counter()
                    #print(end - start)
                
                print("--------")