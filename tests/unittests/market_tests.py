import sys, os
import unittest
sys.path.append('../../application')
import binance_client
import binance_market_client
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
        asset_object = binance_client.Asset(self.client,"ADA")
        self.market_object = binance_market_client.Market(asset_object)

    def test_market_good(self):
        self.market_object.average_price_last_week = 101
        self.market_object.average_price_last_hours = 100
        self.market_object.average_price_last_period = 97.9
        self.market_object.asset_object.price = 97.2
        self.market_object.asset_object.gbp_price = 97.2
        self.market_object.asset_object.avaiable_cash = 1000
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.98990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.market_object.asset_object.purchase_amount = 5

        # Tests that market is good to buy
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(5) == 0.05)
        self.market_object.asset_object.purchase_amount = 0.05
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertTrue(self.market_object.market_good_for_buying())
        self.assertTrue(self.market_object.is_buy_time())

    def test_market_good_1(self):
        self.market_object.average_price_last_week = 101
        self.market_object.average_price_last_hours = 100
        self.market_object.average_price_last_period = 95.9
        self.market_object.asset_object.price = 98.2
        self.market_object.asset_object.gbp_price = 98.2
        self.market_object.asset_object.avaiable_cash = 500
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.98990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.market_object.asset_object.purchase_amount = 5
        
        # Make sure that it wont try to buy
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(5) == 0.05)
        self.market_object.asset_object.purchase_amount = 0.05
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertFalse(self.market_object.market_good_for_buying())
        self.assertFalse(self.market_object.is_buy_time())

    def test_market_good_2(self):
        self.market_object.average_price_last_week = 101
        self.market_object.average_price_last_hours = 100
        self.market_object.average_price_last_period = 99.1
        self.market_object.asset_object.price = 97.99
        self.market_object.asset_object.gbp_price = 97.99
        self.market_object.asset_object.avaiable_cash = 1000
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.98990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.market_object.asset_object.purchase_amount = 5
        
        # Make sure it will buy
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(5) == 0.05)
        self.market_object.asset_object.purchase_amount = 0.05
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertTrue(self.market_object.market_good_for_buying())
        self.assertTrue(self.market_object.is_buy_time())

    def test_market_good_3(self):
        self.market_object.average_price_last_week = 101
        self.market_object.average_price_last_hours = 100
        self.market_object.average_price_last_period = 99.1
        self.market_object.asset_object.price = 99
        self.market_object.asset_object.gbp_price = 99
        self.market_object.asset_object.avaiable_cash = 1000
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.98990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.market_object.asset_object.purchase_amount = 5
        
        #Market is not good for buying
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(5) == 0.05)
        self.market_object.asset_object.purchase_amount = 0.05
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertFalse(self.market_object.is_buy_time())
        self.assertFalse(self.market_object.market_good_for_buying())

    def test_market_good_4(self):
        self.market_object.average_price_last_week = 101
        self.market_object.average_price_last_hours = 100
        self.market_object.average_price_last_period = 97.1
        self.market_object.asset_object.price = 96.99
        self.market_object.asset_object.gbp_price = 96.99
        self.market_object.asset_object.avaiable_cash = 1000
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.98990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.market_object.asset_object.purchase_amount = 5

        # Make sure it wont buy due to average_price_last_period price too high
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(5) == 0.05)
        self.market_object.asset_object.purchase_amount = 0.05
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertFalse(self.market_object.is_buy_time())
        self.assertFalse(self.market_object.market_good_for_buying())

    def test_market_good_5(self):
        self.market_object.average_price_last_week = 101
        self.market_object.average_price_last_hours = 100
        self.market_object.average_price_last_period = 97.9
        self.market_object.asset_object.price = 92.2
        self.market_object.asset_object.gbp_price = 92.2
        self.market_object.asset_object.avaiable_cash = 400
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.98990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.market_object.asset_object.purchase_amount = 410

        # Make sure it wont try to buy when market is good due to lack of cash
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(410) == 4.45)
        self.market_object.asset_object.purchase_amount = 4.45
        self.assertFalse(self.market_object.asset_object.enough_avaiable_cash())
        self.assertFalse(self.market_object.is_buy_time())
        self.assertTrue(self.market_object.market_good_for_buying())

    def test_market_good_6(self):
        self.market_object.average_price_last_week = 101
        self.market_object.average_price_last_hours = 100
        self.market_object.average_price_last_period = 97.9
        self.market_object.asset_object.price = 98.5
        self.market_object.asset_object.gbp_price = 98.5
        self.market_object.asset_object.avaiable_cash = 1000
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.98990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.market_object.asset_object.purchase_amount = 500
        # Make sure it wont buy due to price too high
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(500) == 5.08)
        self.market_object.asset_object.purchase_amount = 5.08
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertFalse(self.market_object.is_buy_time())
        self.assertFalse(self.market_object.market_good_for_buying())


    def test_market_good_7(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.97990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.95990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.93990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.91990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.market_object.average_price_last_week = 1
        self.market_object.average_price_last_hours = 0.97
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.average_price_last_period = 0.96
        self.market_object.asset_object.price = 0.8799
        self.market_object.asset_object.gbp_price = 0.8799
        self.market_object.asset_object.avaiable_cash = 1000
        self.market_object.asset_object.asset_holdings = 51
        self.market_object.asset_object.purchase_amount = 500

        # Make sure that it market is good and double down
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(500) == 568.25)
        self.market_object.asset_object.purchase_amount = 568.25
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertTrue(self.market_object.double_down())
        self.assertTrue(self.market_object.is_buy_time())
        self.assertTrue(self.market_object.market_good_for_buying())

    def test_average_price_3_mins(self):
        data_set = self.get_test_set_hours("3_minutes")
        average_price = self.market_object.get_average_price(data_set)
        self.assertTrue(average_price == 25142.49)

    def test_average_price_3_hours(self):
        data_set = self.get_test_set_hours("3_hours")
        average_price = self.market_object.get_average_price(data_set)
        self.assertTrue(average_price == 25267.794944)

    def test_average_price_3_hours_2(self):
        data_set = self.get_test_set_hours("3_hours_2")
        average_price = self.market_object.get_average_price(data_set)
        self.assertTrue(average_price == 25498.71)

if __name__ == '__main__':
    unittest.main()