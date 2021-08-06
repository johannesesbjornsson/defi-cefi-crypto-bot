import sys, os
import unittest
sys.path.append('../../application')
sys.path.append('../historical_data')
import binance_client
import binance_market_client
import warnings
import datetime
import json
from binance.exceptions import BinanceAPIException
import application_config as cfg
import run_history

class TestingAsset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestingAsset, cls).setUpClass()
        cls.setUpClient(cls)

    def get_test_set_hours(self,data_set):
        with open('test_data/'+data_set+'.json') as f:
            data = json.load(f)
        return data

    def setUpClient(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.client = binance_client.get_client(cfg.api_key,cfg.api_secret)
        currency = "BTC"
        purchase_amount = 50
        asset_object = binance_client.Asset(self.client,currency, purchase_amount=purchase_amount) 
        self.market_object = binance_market_client.Market(asset_object)


    def test_average_price_of_historical_data(self):
        data_set = self.get_test_set_hours("historical_data")
        average_price = self.market_object.get_average_price(data_set)
        
        self.assertTrue(average_price == 24994.505495)

    def test_historical_data(self):
        starting_cash = 1500
        data_set = self.get_test_set_hours("historical_data")
        purchase_amount = 50
        dates, values, action_dates, total_profits, avaiable_cash, postion_worth = run_history.main(data_set,self.market_object,starting_cash,purchase_amount)
        self.assertTrue(total_profits == 2.083)
        self.assertTrue(len(action_dates) == 2)
        self.assertTrue(avaiable_cash == 1502.083)

if __name__ == '__main__':
    unittest.main()