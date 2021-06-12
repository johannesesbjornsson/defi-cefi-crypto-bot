import sys, os
import unittest
sys.path.append('../application')
import binance_client
import warnings
import datetime
import json
from binance.exceptions import BinanceAPIException
import application_config as cfg

class TestingAsset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestingAsset, cls).setUpClass()
        cls.setUpClient(cls)
    
    def setUpClient(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.client = binance_client.get_client(cfg.api_key,cfg.api_secret)
        self.asset_object = binance_client.Asset(self.client,"ADA",2)

    def test_round_down(self):
        rounded_down_number = self.asset_object.round_down(359.499)
        self.assertTrue(rounded_down_number == 359.49)

    def test_active_orders(self):
        order_date = (datetime.datetime.now()-datetime.timedelta(seconds=150)).timestamp()
        epoch_format = int(order_date*1000)
        self.asset_object.orders = [
            {'symbol': 'XRPGBP', 'orderId': 1337, 'orderListId': -1, 'clientOrderId': 'UjWILxew4BkBTAtANYYY3X', 'price': '0.71199000', 'origQty': '72.20000000', 'executedQty': '72.20000000', 'cummulativeQuoteQty': '49.86276400', 'status': 'NEW', 'timeInForce': 'FOK', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': epoch_format, 'updateTime': 1622783728327, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.assertTrue(self.asset_object.has_active_orders())

    def test_active_orders(self):
        order_date = (datetime.datetime.now()-datetime.timedelta(seconds=200)).timestamp()
        epoch_format = int(order_date*1000)
        self.asset_object.orders = [
            {'symbol': 'XRPGBP', 'orderId': 1337, 'orderListId': -1, 'clientOrderId': 'UjWILxew4BkBTAtANYYY3X', 'price': '0.71199000', 'origQty': '72.20000000', 'executedQty': '72.20000000', 'cummulativeQuoteQty': '49.86276400', 'status': 'NEW', 'timeInForce': 'FOK', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': epoch_format, 'updateTime': 1622783728327, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        with self.assertRaises(BinanceAPIException):
            self.asset_object.has_active_orders()
        
    def test_unsold_orders_1(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'v7DM8lYE6rzVEzxj9VQBxq', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693373, 'orderListId': -1, 'clientOrderId': 'EZPskD7ciqhgokM3j1xdxE', 'price': '1.22370000', 'origQty': '81.46000000', 'executedQty': '81.46000000', 'cummulativeQuoteQty': '99.68260200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886438499, 'updateTime': 1622886445108, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693590, 'orderListId': -1, 'clientOrderId': 'dqirtCnmPRb34djiEEn6a6', 'price': '1.22690000', 'origQty': '40.75000000', 'executedQty': '40.75000000', 'cummulativeQuoteQty': '49.98802500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886472913, 'updateTime': 1622886472913, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.assertTrue(len(self.asset_object.get_unsold_orders()) == 1)

    def test_unsold_orders_2(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'v7DM8lYE6rzVEzxj9VQBxq', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693373, 'orderListId': -1, 'clientOrderId': 'EZPskD7ciqhgokM3j1xdxE', 'price': '1.22370000', 'origQty': '81.46000000', 'executedQty': '81.46000000', 'cummulativeQuoteQty': '99.68260200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886438499, 'updateTime': 1622886445108, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693590, 'orderListId': -1, 'clientOrderId': 'dqirtCnmPRb34djiEEn6a6', 'price': '1.22690000', 'origQty': '40.75000000', 'executedQty': '40.75000000', 'cummulativeQuoteQty': '49.98802500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886472913, 'updateTime': 1622886472913, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.assertTrue(len(self.asset_object.get_unsold_orders()) == 2)

    def test_unsold_orders_3(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'v7DM8lYE6rzVEzxj9VQBxq', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693373, 'orderListId': -1, 'clientOrderId': 'EZPskD7ciqhgokM3j1xdxE', 'price': '1.22370000', 'origQty': '81.46000000', 'executedQty': '81.46000000', 'cummulativeQuoteQty': '99.68260200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886438499, 'updateTime': 1622886445108, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693590, 'orderListId': -1, 'clientOrderId': 'dqirtCnmPRb34djiEEn6a6', 'price': '1.22690000', 'origQty': '40.75000000', 'executedQty': '40.75000000', 'cummulativeQuoteQty': '49.98802500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886472913, 'updateTime': 1622886472913, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.assertTrue(len(self.asset_object.get_unsold_orders()) == 4)

    def test_unsold_orders_4(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'v7DM8lYE6rzVEzxj9VQBxq', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'v7DM8lYE6rzVEzxj9VQBxq', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'CANCELLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693373, 'orderListId': -1, 'clientOrderId': 'EZPskD7ciqhgokM3j1xdxE', 'price': '1.22370000', 'origQty': '81.46000000', 'executedQty': '81.46000000', 'cummulativeQuoteQty': '99.68260200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886438499, 'updateTime': 1622886445108, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693590, 'orderListId': -1, 'clientOrderId': 'dqirtCnmPRb34djiEEn6a6', 'price': '1.22690000', 'origQty': '40.75000000', 'executedQty': '40.75000000', 'cummulativeQuoteQty': '49.98802500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886472913, 'updateTime': 1622886472913, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'v7DM8lYE6rzVEzxj9VQBxq', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'CANCELLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.assertTrue(len(self.asset_object.get_unsold_orders()) == 4)

    def test_double_down_1(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.asset_object.avaiable_cash = 51
        self.asset_object.price = 0.9599
        self.assertTrue(self.asset_object.double_down())

    def test_double_down_2(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.asset_object.avaiable_cash = 49
        self.asset_object.price = 0.9599
        self.assertFalse(self.asset_object.double_down())

    def test_double_down_3(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.95990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.asset_object.avaiable_cash = 51
        self.asset_object.price = 0.9200
        self.assertFalse(self.asset_object.double_down())

    def test_double_down_4(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.95990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.asset_object.avaiable_cash = 51
        self.asset_object.price = 0.9199
        self.assertTrue(self.asset_object.double_down())

    def test_double_down_5(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.95990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.91990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.asset_object.avaiable_cash = 51
        self.asset_object.price = 0.879
        self.assertTrue(self.asset_object.double_down())

    def test_double_down_6(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.95990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.91990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.91990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.asset_object.avaiable_cash = 51
        self.asset_object.price = 0.839
        self.assertTrue(self.asset_object.double_down())

    def test_double_down_7(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.95990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.91990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.91990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.91990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.asset_object.avaiable_cash = 51
        self.asset_object.price = 0.75
        self.assertFalse(self.asset_object.double_down())

    def test_double_down_8(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.95990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.91990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.91990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'xCJh7QDEH5AeC3liBomaej', 'price': '0.91990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.asset_object.avaiable_cash = 51
        self.asset_object.price = 0.84
        self.assertFalse(self.asset_object.double_down())

    def test_buy_asset(self):
        order = self.asset_object.test_buy_asset()
        self.assertFalse(order)

if __name__ == '__main__':
    unittest.main()