import sys, os
import unittest
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
        self.token_static = self.token_pair

    # Testing if my custom liquidity analysis to get price
    def test_liquidity_analysis(self):
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


if __name__ == '__main__':
    unittest.main()