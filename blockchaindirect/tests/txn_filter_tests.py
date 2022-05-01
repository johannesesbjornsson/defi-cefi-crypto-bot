import sys, os, json
import unittest
import copy
import random
sys.path.append('../libraries')
from blockchain_client import Client
from tokens import Token
from transaction import Transaction, RouterTransaction
from triggers import Triggers
from token_pair import TokenPair
from transaction_scanner import TransactionScanner, TransactionFilter


class TxnFilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TxnFilter, cls).setUpClass()
        cls.setUpClient(cls)

    def setUpClient(self):
        my_address=os.environ['my_address']
        api_key=os.environ['api_key']
        node_key = os.environ['moralis_node_key']
        self.polygon_client = Client("polygon", my_address, "dummy_private_key", node_key, api_key )
       

    # Testing txn filter for router txns
    def test_router_txn_filtering(self):
        txn_hash_1 = "0xc2f5b9c51f0702e2eab981ff7dfeb68d16a02e2f7ea807e1d1b9b0e0f585a417"
        transaction_info_1 = self.polygon_client.web3.eth.get_transaction(txn_hash_1)
        txn_1 = Transaction(self.polygon_client,transaction_info_1)

        txn_hash_2 = "0xd1862c6753685693822f3c17bdf557711eee5bad59917312e671690a68f30d75"
        transaction_info_2 = self.polygon_client.web3.eth.get_transaction(txn_hash_2)
        txn_2 = Transaction(self.polygon_client,transaction_info_2)

        
        txn_filter = TransactionFilter(self.polygon_client)

        txn_filter.create_router_filter(function_matcher_method="startswith",function_name="swap",block_number=27790965,minimum_gas_price=self.polygon_client.minimum_gas_price, token_hash=self.polygon_client.token_to_scan_for)
        
        matching_txn_1 = txn_filter.get_single_matching_transaction(txn_1)
        matching_txn_2 = txn_filter.get_single_matching_transaction(txn_2)

        txn_filter_2 = TransactionFilter(self.polygon_client)
        txn_filter_2.create_router_filter(function_matcher_method="is",function_name="swapExactTokensForTokens",block_number=27790965,minimum_gas_price=self.polygon_client.minimum_gas_price, token_hash=self.polygon_client.token_to_scan_for)
        matching_txn_3 = txn_filter_2.get_single_matching_transaction(txn_1)

        txn_filter_3 = TransactionFilter(self.polygon_client)
        txn_filter_3.create_router_filter(function_matcher_method="startswith",function_name="w",block_number=27790965,minimum_gas_price=self.polygon_client.minimum_gas_price, token_hash=self.polygon_client.token_to_scan_for)
        matching_txn_4 = txn_filter_3.get_single_matching_transaction(txn_1)

        txn_filter_4 = TransactionFilter(self.polygon_client)
        txn_filter_4.create_router_filter(function_matcher_method="contains",function_name="ExactTokens",block_number=27790965,minimum_gas_price=self.polygon_client.minimum_gas_price, token_hash=self.polygon_client.token_to_scan_for)
        matching_txn_5 = txn_filter_4.get_single_matching_transaction(txn_1)

        self.assertTrue(str(matching_txn_1) == txn_1.hash)
        self.assertTrue(matching_txn_2 is None)
        self.assertTrue(str(matching_txn_3) == txn_1.hash)
        self.assertTrue(matching_txn_4 is None)
        self.assertTrue(str(matching_txn_5) == txn_1.hash)


if __name__ == '__main__':
    unittest.main()