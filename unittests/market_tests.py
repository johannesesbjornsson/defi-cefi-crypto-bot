import sys, os
import unittest
sys.path.append('../application')
import binance_client
import warnings
import datetime
import json
from binance.exceptions import BinanceAPIException
import application_config as cfg


class TestingMarket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestingMarket, cls).setUpClass()
        cls.setUpClient(cls)

    # def setUp(self):
    #     sys.stdout = open(os.devnull, 'w')

    # def tearDown(self):
    #     sys.stdout.close()
    #     sys.stdout = sys.__stdout__

    def get_test_set_hours(self,data_set):
        with open('test_data/'+data_set+'.json') as f:
            data = json.load(f)
        return data

    def setUpClient(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.client = binance_client.get_client(cfg.api_key,cfg.api_secret)
        asset_object = binance_client.Asset(self.client,"ADA",2)
        self.market_object = binance_client.Market(asset_object)

    def test_market_good(self):
        self.market_object.average_price_last_week =100
        self.market_object.average_price_thee_hour = 100
        self.market_object.average_price_last_period = 98.9
        self.market_object.asset_object.price = 98.2
        self.market_object.asset_object.avaiable_cash = 1000

        self.assertTrue(self.market_object.is_buy_time())

    def test_market_good_1(self):
        self.market_object.average_price_last_week =100
        self.market_object.average_price_thee_hour = 100
        self.market_object.average_price_last_period = 98.9
        self.market_object.asset_object.price = 98.2
        self.market_object.asset_object.avaiable_cash = 49

        self.assertFalse(self.market_object.is_buy_time())

    def test_market_good_2(self):
        self.market_object.average_price_last_week = 100
        self.market_object.average_price_thee_hour = 100
        self.market_object.average_price_last_period = 99.1
        self.market_object.asset_object.price = 98
        self.market_object.asset_object.avaiable_cash = 1000
        self.assertTrue(self.market_object.is_buy_time())

    def test_market_bad(self):
        self.market_object.average_price_last_week = 100
        self.market_object.average_price_thee_hour = 100
        self.market_object.average_price_last_period = 99.1
        self.market_object.asset_object.price = 99
        self.market_object.asset_object.avaiable_cash = 1000
        self.assertFalse(self.market_object.is_buy_time())

    def test_market_price_to_high(self):
        self.market_object.average_price_last_week = 100
        self.market_object.average_price_thee_hour = 100
        self.market_object.average_price_last_period = 98.9
        self.market_object.asset_object.price = 98.5
        self.market_object.asset_object.avaiable_cash = 1000
        self.assertFalse(self.market_object.is_buy_time())

    def test_average_price_3_mins(self):
        data_set = self.get_test_set_hours("3_minutes")
        average_price = self.market_object.get_average_price(data_set)
        self.assertTrue(average_price == 25142.49)

    def test_average_price_3_hours(self):
        data_set = self.get_test_set_hours("3_hours")
        average_price = self.market_object.get_average_price(data_set)
        self.assertTrue(average_price == 25267.79494444444)

    def test_average_price_3_hours_2(self):
        data_set = self.get_test_set_hours("3_hours_2")
        average_price = self.market_object.get_average_price(data_set)
        self.assertTrue(average_price == 25498.709999999966)

if __name__ == '__main__':
    unittest.main()