import sys, os, json
import unittest
import copy
import random
import logging
sys.path.append('../libraries')
from blockchain_client import Client
from tokens import Token
from transaction import Transaction, RouterTransaction
from triggers import Triggers
from token_pair import TokenPair


class TokenTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TokenTest, cls).setUpClass()
        cls.setUpClient(cls)

    def setUpClient(self):
        my_address=os.environ['my_address']
        api_key=os.environ['api_key']
        node_key = os.environ['moralis_node_key']
        logger = logging.getLogger("unittests")
        logger.setLevel(logging.INFO)
        self.polygon_client = Client("polygon", my_address, "dummy_private_key", node_key, logger, api_key )
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
        self.assertTrue(difference > 0.9998 and difference < 1.0002)

        token_2_amount_in = self.token_2.to_wei(1000)
        amount_out_contract = self.token_pair.get_amount_token_1_out(token_2_amount_in)
        amount_out_offline = self.token_pair.get_amount_token_1_out(token_2_amount_in, offline_calculation=True)
        difference = amount_out_contract/amount_out_offline 
        self.assertTrue(difference > 0.9998 and difference < 1.0002)        

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

        # Test getting amount in by liquidity impact 
        amount_in_token_1 = self.token_pair_static.get_amount_in_from_liquidity_impact_of_token_1_for_token_2(0.05)
        amount_in_token_2 = self.token_pair_static.get_amount_in_from_liquidity_impact_of_token_2_for_token_1(0.05)
        self.assertTrue(amount_in_token_1 == 1000)
        self.assertTrue(amount_in_token_2 == 500)
    
    # Tests random locally stored token infro matches blockchain stored info
    def test_z_file_init(self):
        pair_list = random.sample(self.polygon_client.pair_info.keys() , 3)
        for pair in pair_list:
            token_address_1, token_address_2 = pair.split("_")
            
            token_1 = Token(self.polygon_client, token_address_1)
            token_2 = Token(self.polygon_client, token_address_2)
            token_pair = TokenPair(self.polygon_client, token_1, token_2)

            local_token_1 = Token(self.polygon_client, token_address_1, "local")
            local_token_2 = Token(self.polygon_client, token_address_2, "local")
            local_token_pair = TokenPair(self.polygon_client, token_1, token_2, "local")
            token_1_amount_in = self.token_1.to_wei(100)

            amount_out = token_pair.get_amount_token_2_out(token_1_amount_in, offline_calculation=True)
            local_amount_out = local_token_pair.get_amount_token_2_out(token_1_amount_in, offline_calculation=True)

            try:
                difference = amount_out/local_amount_out
                self.assertTrue(difference > 0.9998 and difference < 1.0002)
            except ZeroDivisionError as e:
                pass

            self.assertTrue(token_1.decimals == local_token_1.decimals)
            self.assertTrue(token_2.decimals == local_token_2.decimals)
            self.assertTrue(token_pair.liquidity_pool_address == local_token_pair.liquidity_pool_address)
            self.assertTrue(token_pair.raw_reserves_token_1 == local_token_pair.raw_reserves_token_1)
            

            

if __name__ == '__main__':
    unittest.main()