import sys, os
import unittest
import copy
sys.path.append('../libraries')
from eth_fork_client import Client
from eth_fork_token import Token
from eth_fork_transaction import Transaction, RouterTransaction
from eth_fork_triggers import Triggers
from eth_fork_token_pair import TokenPair


class TokenTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TokenTest, cls).setUpClass()
        cls.setUpClient(cls)

    def setUpClient(self):
        my_address=os.environ['my_address']
        self.polygon_client = Client("polygon", my_address, "dummy_private_key")
        self.token_1 = Token(self.polygon_client, "USDC")
        self.token_2 = Token(self.polygon_client, "WMATIC")
        self.token_pair = TokenPair(self.polygon_client, self.token_1, self.token_2)
        self.token_pair_static = copy.copy(self.token_pair)
        self.token_pair_static.token_1_liquidity = 20000
        self.token_pair_static.token_2_liquidity = 10000

    # Testing if my cusstom way to get price
    def test_get_price(self):
        token_1_amount_in = self.token_1.to_wei(1000)
        amount_out_contract = self.token_pair.get_amount_token_2_out(token_1_amount_in)
        amount_out_offline = self.token_pair.get_amount_token_2_out(token_1_amount_in, offline_calculation=True)
        difference = amount_out_contract/amount_out_offline
        self.assertTrue(difference > 0.9999 and difference < 1.0001)

        token_2_amount_in = self.token_2.to_wei(1000)
        amount_out_contract = self.token_pair.get_amount_token_1_out(token_2_amount_in)
        amount_out_offline = self.token_pair.get_amount_token_1_out(token_2_amount_in, offline_calculation=True)
        difference = amount_out_contract/amount_out_offline 
        self.assertTrue(difference > 0.9999 and difference < 1.0001)        

    # Testing my liquidity analysis functions
    def test_liquidity_impact(self):
        #Testing get_amount_out
        token_1_amount_in = self.token_1.to_wei(1000)
        amount_out_offline = self.token_pair_static.get_amount_token_2_out(token_1_amount_in, offline_calculation=True)
        self.assertTrue(amount_out_offline == 474761904761905610752)

        # Test liqudity impact
        liquidity_impact_1 = self.token_pair_static.get_liquidity_impact_of_token_1_for_token_2(1000)
        liquidity_impact_2 = self.token_pair_static.get_liquidity_impact_of_token_2_for_token_1(1000)
        self.assertTrue(liquidity_impact_1 == 0.05)
        self.assertTrue(liquidity_impact_2 == 0.1)
    
    # Test handling of transaction it should not handle
    def test_txn_analysis_1(self):
        txn_hash_1 = "0x9f06175fbc443250187f5b3003d12ac864c3580afcfc48f27955bdf4617f024c"
        transaction_info = self.polygon_client.web3.eth.get_transaction(txn_hash_1)
        txn = Transaction(self.polygon_client,transaction_info)
        router_txn = RouterTransaction(txn)
        liquidity_impact, txn_value = self.token_pair_static.quick_router_transction_analysis(router_txn)
        self.assertTrue(liquidity_impact == 0 and txn_value == 0)

    # Test test hadnling of tokens in middle of hop (cant use in or out amount)
    def test_txn_analysis_2(self):
        txn_hash_1 = "0xd550d11083d5a273d0cee387358e2d44fef199e23ad5f61957c9b1521ff57146"
        transaction_info = self.polygon_client.web3.eth.get_transaction(txn_hash_1)
        txn = Transaction(self.polygon_client,transaction_info)
        router_txn = RouterTransaction(txn)
        liquidity_impact, txn_value = self.token_pair_static.quick_router_transction_analysis(router_txn)
        self.assertTrue(liquidity_impact == 0 and txn_value == 0)

    # Test amount in without hops
    def test_txn_analysis_3(self):
        txn_hash_1 = "0x4b28cc27f73fab2906a96b3380b0d53224b4f364c8e3bfd0d87008bf6ccb9d8c"
        transaction_info = self.polygon_client.web3.eth.get_transaction(txn_hash_1)
        txn = Transaction(self.polygon_client,transaction_info)
        router_txn = RouterTransaction(txn)
        liquidity_impact, txn_value = self.token_pair_static.quick_router_transction_analysis(router_txn)
        self.assertTrue(liquidity_impact == 0.0001 and txn_value == 2)

    # Test amount out with multi hop
    def test_txn_analysis_4(self):
        txn_hash_1 = "0x21f3acf137016e7e9157fa50c78685d296f3759fc6ab6edecbab03f40cf01846"
        transaction_info = self.polygon_client.web3.eth.get_transaction(txn_hash_1)
        txn = Transaction(self.polygon_client,transaction_info)
        router_txn = RouterTransaction(txn)
        liquidity_impact, txn_value = self.token_pair_static.quick_router_transction_analysis(router_txn)
        self.assertTrue(round(liquidity_impact, 5) == 0.00313 and round(txn_value, 5)  == 62.53272)

    # Testing exact amount in with multi path swap
    def test_txn_analysis_5(self):
        txn_hash_1 = "0xb33d68afbbfb7979af47ed996d3e38b677d3f6b64d0f6877aed0d71df09033ca"
        transaction_info = self.polygon_client.web3.eth.get_transaction(txn_hash_1)
        txn = Transaction(self.polygon_client,transaction_info)
        router_txn = RouterTransaction(txn)
        liquidity_impact, txn_value = self.token_pair_static.quick_router_transction_analysis(router_txn)
        self.assertTrue(round(liquidity_impact, 5) == 0.2 and round(txn_value, 5)  == 4000)

    # Testing max amount in with multi path swap
    def test_txn_analysis_6(self):
        txn_hash_1 = "0xc40c4206fea214137434ee429ee8959301c0f25983271e56eb4cbd002966315a"
        transaction_info = self.polygon_client.web3.eth.get_transaction(txn_hash_1)
        txn = Transaction(self.polygon_client,transaction_info)
        router_txn = RouterTransaction(txn)
        liquidity_impact, txn_value = self.token_pair_static.quick_router_transction_analysis(router_txn)
        self.assertTrue(round(liquidity_impact, 5) == 0.00022 and round(txn_value, 5)  == 4.44855)

if __name__ == '__main__':
    unittest.main()