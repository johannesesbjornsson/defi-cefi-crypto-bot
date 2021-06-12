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

    def setUp(self):
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = sys.__stdout__

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
        print(average_price)
        self.assertTrue(average_price == 25142.49)

    def test_average_price_3_hours(self):
        data_set = self.get_test_set_hours("3_hours")
        average_price = self.market_object.get_average_price(data_set)
        self.assertTrue(average_price == 25267.79494444444)

    def test_average_price_3_hours_2(self):
        data_set = self.get_test_set_hours("3_hours_2")
        average_price = self.market_object.get_average_price(data_set)
        self.assertTrue(average_price == 25498.709999999966)


class TestingAsset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestingAsset, cls).setUpClass()
        cls.setUpClient(cls)

    def setUp(self):
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = sys.__stdout__
    
    def setUpClient(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.client = binance_client.get_client(cfg.api_key,cfg.api_secret)
        self.asset_object = binance_client.Asset(self.client,"ADA",2)

    def test_purchase_price_1(self):
        self.asset_object.orders = [
            {'symbol': 'XRPGBP', 'orderId': 74741223, 'orderListId': -1, 'clientOrderId': 'UjWILxew4BkBTAtANYYY3X', 'price': '0.69199000', 'origQty': '72.20000000', 'executedQty': '72.20000000', 'cummulativeQuoteQty': '49.86276400', 'status': 'FILLED', 'timeInForce': 'FOK', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622783728327, 'updateTime': 1622783728327, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'XRPGBP', 'orderId': 74741223, 'orderListId': -1, 'clientOrderId': 'UjWILxew4BkBTAtANYYY3X', 'price': '0.60199000', 'origQty': '72.20000000', 'executedQty': '72.20000000', 'cummulativeQuoteQty': '49.86276400', 'status': 'FILLED', 'timeInForce': 'FOK', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622783728327, 'updateTime': 1622783728327, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]        
        self.assertTrue(self.asset_object.get_purchase_price() == 0.69199000)    

    def test_purchase_price_2(self):
        self.asset_object.orders = [
            {'symbol': 'ETHGBP', 'orderId': 191053235, 'orderListId': -1, 'clientOrderId': 'A2YM4pm4BKY7shAs0CN5UA', 'price': '1849.24000000', 'origQty': '0.02700000', 'executedQty': '0.02700000', 'cummulativeQuoteQty': '49.92948000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622791494212, 'updateTime': 1622791501497, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ETHGBP', 'orderId': 192101225, 'orderListId': -1, 'clientOrderId': 'gfCQJOoHiyNGV3JmjRjRMr', 'price': '1981.71000000', 'origQty': '0.02790000', 'executedQty': '0.02790000', 'cummulativeQuoteQty': '55.28970900', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622882417375, 'updateTime': 1622882417396, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ETHGBP', 'orderId': 192326632, 'orderListId': -1, 'clientOrderId': 'FaOJAyctI8pOuiCgRqE33h', 'price': '1869.66000000', 'origQty': '0.02670000', 'executedQty': '0.02670000', 'cummulativeQuoteQty': '49.91992200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622898728728, 'updateTime': 1622898736773, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]        
        self.assertTrue(self.asset_object.get_purchase_price() == 1869.66000000)    

    def test_purchase_price_3(self):
        self.asset_object.orders = [
            {'symbol': 'BTCGBP', 'orderId': 204045611, 'orderListId': -1, 'clientOrderId': 'riPN2pYRDmASabWV17nDKr', 'price': '0.00000000', 'origQty': '0.00181100', 'executedQty': '0.00181100', 'cummulativeQuoteQty': '49.99792501', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622141089336, 'updateTime': 1622141089336, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]        
        self.assertTrue(self.asset_object.get_purchase_price() == 27607.910000000003)   

    def test_purchase_price_4(self):
        self.asset_object.orders = [
            {'symbol': 'ETHGBP', 'orderId': 192101225, 'orderListId': -1, 'clientOrderId': 'gfCQJOoHiyNGV3JmjRjRMr', 'price': '1981.71000000', 'origQty': '0.02790000', 'executedQty': '0.02790000', 'cummulativeQuoteQty': '55.28970900', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622882417375, 'updateTime': 1622882417396, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ETHGBP', 'orderId': 192326632, 'orderListId': -1, 'clientOrderId': 'FaOJAyctI8pOuiCgRqE33h', 'price': '1869.66000000', 'origQty': '0.02670000', 'executedQty': '0.02670000', 'cummulativeQuoteQty': '49.91992200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622898728728, 'updateTime': 1622898736773, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]        
        self.assertTrue(self.asset_object.get_purchase_price() == 1981.71000000)

    def test_purchase_price_5(self):
        self.asset_object.orders = [
            {'symbol': 'BTCGBP', 'orderId': 204045611, 'orderListId': -1, 'clientOrderId': 'riPN2pYRDmASabWV17nDKr', 'price': '0.00000000', 'origQty': '0.00181100', 'executedQty': '0.00181100', 'cummulativeQuoteQty': '49.99792501', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622141089336, 'updateTime': 1622141089336, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ETHGBP', 'orderId': 192326632, 'orderListId': -1, 'clientOrderId': 'FaOJAyctI8pOuiCgRqE33h', 'price': '1869.66000000', 'origQty': '0.02670000', 'executedQty': '0.02670000', 'cummulativeQuoteQty': '49.91992200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622898728728, 'updateTime': 1622898736773, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]        
        self.assertTrue(self.asset_object.get_purchase_price() == 27607.910000000003) 


    def test_is_sell_time_1(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'v7DM8lYE6rzVEzxj9VQBxq', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.asset_object.price = 1.22370000
        self.assertFalse(self.asset_object.is_sell_time())

    def test_is_sell_time_2(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'v7DM8lYE6rzVEzxj9VQBxq', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.asset_object.price = 1.26370000
        self.assertTrue(self.asset_object.is_sell_time())

    def test_is_sell_time_3(self):
        self.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'v7DM8lYE6rzVEzxj9VQBxq', 'price': '1.30620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693373, 'orderListId': -1, 'clientOrderId': 'EZPskD7ciqhgokM3j1xdxE', 'price': '1.32370000', 'origQty': '81.46000000', 'executedQty': '81.46000000', 'cummulativeQuoteQty': '99.68260200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886438499, 'updateTime': 1622886445108, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693590, 'orderListId': -1, 'clientOrderId': 'dqirtCnmPRb34djiEEn6a6', 'price': '1.22690000', 'origQty': '40.75000000', 'executedQty': '40.75000000', 'cummulativeQuoteQty': '49.98802500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886472913, 'updateTime': 1622886472913, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.asset_object.price = 1.26470000
        self.assertTrue(self.asset_object.is_sell_time())

    def test_is_sell_time_4(self):
        self.asset_object.orders = [
            {'symbol': 'XRPGBP', 'orderId': 72969141, 'orderListId': -1, 'clientOrderId': 'mTsKcGIHwzuN7jaay6a00J', 'price': '0.68000000', 'origQty': '81.10000000', 'executedQty': '81.10000000', 'cummulativeQuoteQty': '49.98274100', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622379153872, 'updateTime': 1622379153872, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'XRPGBP', 'orderId': 73919573, 'orderListId': -1, 'clientOrderId': 'Nbp3JD7IqlnhVAN7LLg16c', 'price': '0.68000000', 'origQty': '72.50000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'CANCELED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622577348632, 'updateTime': 1622655983862, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'XRPGBP', 'orderId': 74741223, 'orderListId': -1, 'clientOrderId': 'UjWILxew4BkBTAtANYYY3X', 'price': '0.51199000', 'origQty': '72.20000000', 'executedQty': '72.20000000', 'cummulativeQuoteQty': '49.86276400', 'status': 'FILLED', 'timeInForce': 'FOK', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622783728327, 'updateTime': 1622783728327, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.asset_object.price = 0.61199000
        self.assertFalse(self.asset_object.is_sell_time())

    def test_is_sell_time_4(self):
        self.asset_object.orders = [
            {'symbol': 'XRPGBP', 'orderId': 73919573, 'orderListId': -1, 'clientOrderId': 'Nbp3JD7IqlnhVAN7LLg16c', 'price': '0.58000000', 'origQty': '72.50000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'CANCELED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622577348632, 'updateTime': 1622655983862, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'XRPGBP', 'orderId': 74741223, 'orderListId': -1, 'clientOrderId': 'UjWILxew4BkBTAtANYYY3X', 'price': '0.71199000', 'origQty': '72.20000000', 'executedQty': '72.20000000', 'cummulativeQuoteQty': '49.86276400', 'status': 'FILLED', 'timeInForce': 'FOK', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622783728327, 'updateTime': 1622783728327, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.asset_object.price = 0.71199000
        self.assertFalse(self.asset_object.is_sell_time())

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
        print(order)
        
        self.assertFalse(order)

if __name__ == '__main__':
    unittest.main()