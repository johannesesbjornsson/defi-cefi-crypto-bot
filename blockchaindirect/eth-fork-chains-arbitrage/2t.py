import asyncio
import time
import sys
import json
import logic
sys.path.insert(0,'../libraries')

from blockchain_client import Client
from tokens import Token
from transaction import Transaction, RouterTransaction
import cfg as cfg

class TransactionFilter(object):
    def __init__(self, client):
        self.client = client
        self.filter = None

    def match_function(self, txn_function):
        if self.function_matcher_method == "is":
            return self.function_name.__eq__(txn_function)
        elif self.function_matcher_method == "startswith":
            return txn_function.startswith(self.function_name)
        elif self.function_matcher_method == "contains":
            return self.function_name in txn_function
        else:
            raise ValueError(f"function_matcher_method '{self.function_matcher_method}' not supported")

    def create_router_filter(self, block_number=None, minimum_gas_price=None, contract_address=None, function_matcher_method="is", function_name=None, token_hash=None):
        self.block_number = block_number
        self.minimum_gas_price = minimum_gas_price
        self.contract_address = contract_address 
        self.filter = RouterTransactionFilter(function_matcher_method, function_name, token_hash)
  

    def get_single_matching_transaction(self,txn):
        matching_txn = None
        if txn.to == self.client.router_contract_address and txn.block_number == self.block_number and txn.gas_price >= self.minimum_gas_price:
            matching_txn = self.filter.get_single_matching_transaction(txn)
        return matching_txn

class RouterTransactionFilter(TransactionFilter):
    def __init__(self,function_matcher_method, function_name, token_hash):
        self.function_matcher_method = function_matcher_method
        self.function_name = function_name
        self.token_hash = token_hash

    def get_single_matching_transaction(self,txn):
        matching_txn = None
        router_txn = RouterTransaction(txn)
        if self.match_function(router_txn.function_called) and self.token_hash in router_txn.path:
            matching_txn = router_txn

        return matching_txn


if __name__ == "__main__":
    client = Client("polygon", cfg.my_address, cfg.private_key, cfg.node_key, cfg.api_key)

    txn_hash_1 = "0xc2f5b9c51f0702e2eab981ff7dfeb68d16a02e2f7ea807e1d1b9b0e0f585a417"
    transaction_info = client.web3.eth.get_transaction(txn_hash_1)
    txn = Transaction(client,transaction_info)

    txn_filter = TransactionFilter(client)
    txn_filter.create_router_filter(function_matcher_method="startswith",function_name="swap",block_number=27790965,minimum_gas_price=client.minimum_gas_price, token_hash=client.token_to_scan_for)
    #txn_filter.create_router_filter(function_matcher_method="contains",function_name="wapExactTokensForTokens",block_number=27790965,minimum_gas_price=client.minimum_gas_price)
    matching_txn = txn_filter.get_single_matching_transaction(txn)
    print(matching_txn)