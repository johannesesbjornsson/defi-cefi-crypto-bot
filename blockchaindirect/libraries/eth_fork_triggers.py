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
        self.token_to_scan_for = self.client.token_to_scan_for
        self.minimum_scanned_transaction = self.client.minimum_scanned_transaction
        self.scan_token_value = self.client.scan_token_value
        self.token_1 = Token(self.client,self.token_to_scan_for)
        self.client.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    def handle_swap_transaction(self, gas_price, txn_input):
        token_pair = None
        amount_in = None
        amount_out = None
        try:
            input_token, out_token = txn_input["path"][:2]
            if input_token == self.token_to_scan_for:
                token_2 = Token(self.client,out_token)
                token_pair = TokenPair(self.client, self.token_1, token_2)

            else:
                token_pair = None
        except ValueError as e:
            token_pair = None
        
        if token_pair:
            if "amountIn" in txn_input:
                txn_amount = self.token_1.from_wei(txn_input["amountIn"])
            elif "amountInMax" in txn_input:
                txn_amount = self.token_1.from_wei(txn_input["amountInMax"])
            else:
                
                if "amountOut" in txn_input:
                    amount_out = txn_input["amountOut"]
                elif "amountOutMin" in txn_input:
                    amount_out = txn_input["amountOutMin"]
                
                if len(txn_input["path"]) == 2:
                    txn_amount = self.token_1.from_wei(token_pair.get_amount_token_1_out(amount_out))
                else:
                    print("unable to get txn amount in")
                    # Find a way to deal with this (when there are three or more tokens)
                    txn_amount = 0

            if txn_amount > self.minimum_scanned_transaction:
                print("Transaction value:",txn_amount)
                amount_in = self.token_1.to_wei(self.scan_token_value)
                amount_out = token_pair.get_amount_token_2_out(amount_in)
                gas_price = gas_price + self.client.web3.toWei('1','gwei')

        return token_pair, amount_in, amount_out, gas_price


    def get_router_contract_interactions(self, tx_filter):
        pending_router_transactions = []
        pending_transactions = tx_filter.get_new_entries()
        for transaction in pending_transactions:
            txn_hash = self.client.web3.toHex(transaction)
            txn = Transaction(self.client, txn_hash)

            if not txn.found_transaction():
                continue
            if txn.to != self.client.router_contract_address or txn.block_number is not None:
                continue
            router_txn = RouterTransaction(txn)
            if router_txn.function_called.startswith("swap"):
                pending_router_transactions.append(router_txn)

        return pending_router_transactions

    #def find_replacement_transaction(self, tx_filter, router_txn):
    #    pending_transactions = tx_filter.get_new_entries()
    #    for transaction in pending_transactions:
    #        txn_hash = self.client.web3.toHex(transaction)
    #        txn = Transaction(self.client, txn_hash)
    #        if not txn.found_transaction():
    #            continue
    #        if txn == router_txn.transaction:
    #            print("Old", router_txn)
    #            print("New", txn)

    def intercept_transactions(self):
        #eth_newPendingTransactionFilter
        tx_filter = self.client.web3_ws.eth.filter('pending')
        intercepted_transaction = False

        
        print("Taking a wee break")
        time.sleep(2)
        pending_transactions = self.get_router_contract_interactions(tx_filter)

        for router_txn in pending_transactions:

            token_pair, amount_in, amount_out, gas_price = self.handle_swap_transaction(router_txn.transaction.gas_price, router_txn.input_data)
            if not token_pair or not amount_in or not amount_out or not gas_price:
                continue
            
            transaction_complete, transaction_successful = router_txn.transaction.get_transaction_receipt(wait=False)
                
            if transaction_complete:
                print("Too slow....")
                print("Transaction successful: ",router_txn.transaction.successful)
                print(router_txn.transaction.hash)
            else:    
                print("Winning!!")
                print(router_txn.transaction.hash)
                intercepted_transaction = True
                #new_tx_filter = self.client.web3_ws.eth.filter('pending')
                #while True:
                #    self.find_replacement_transaction(new_tx_filter,router_txn)

                #amount_out_from_token_2 = token_pair.swap_token_1_for_token_2(amount_in, amount_out, gas_price)
                #token_pair.token_2.approve_token()
                #transaction_complete, transaction_successful = router_txn.transaction.get_transaction_receipt(wait=True)
                #amount_out_from_token_1 = token_pair.get_amount_token_1_out(amount_out_from_token_2)
                #token_pair.swap_token_2_for_token_1(amount_out_from_token_2, amount_out_from_token_1)
                #break
                
                print("--------")