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

class TestingAsset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestingAsset, cls).setUpClass()
        cls.setUpClient(cls)
    
    def setUpClient(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.client = binance_client.get_client(cfg.api_key,cfg.api_secret)
        self.asset_object = binance_client.Asset(self.client,"ADA")
        self.market_object = binance_market_client.Market(self.asset_object)

    def test_purchase_amount(self):
        self.market_object.asset_object.precision = 0.01
        self.market_object.asset_object.price = 1.02127
        self.market_object.asset_object.gbp_price = 1.02127

        # Tests quantity is correct for buy order
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(50) == 48.96)

    def test_active_orders(self):
        order_date = (datetime.datetime.now()-datetime.timedelta(seconds=150)).timestamp()
        epoch_format = int(order_date*1000)
        self.market_object.asset_object.orders = [
            {'symbol': 'XRPGBP', 'orderId': 1337, 'orderListId': -1, 'clientOrderId': 'UjWILxew4BkBTAtANYYY3X', 'price': '0.71199000', 'origQty': '72.20000000', 'executedQty': '72.20000000', 'cummulativeQuoteQty': '49.86276400', 'status': 'NEW', 'timeInForce': 'FOK', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': epoch_format, 'updateTime': 1622783728327, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.assertTrue(self.market_object.asset_object.has_active_orders())

    def test_active_orders(self):
        order_date = (datetime.datetime.now()-datetime.timedelta(seconds=200)).timestamp()
        epoch_format = int(order_date*1000)
        self.market_object.asset_object.orders = [
            {'symbol': 'XRPGBP', 'orderId': 1337, 'orderListId': -1, 'clientOrderId': 'UjWILxew4BkBTAtANYYY3X', 'price': '0.71199000', 'origQty': '72.20000000', 'executedQty': '72.20000000', 'cummulativeQuoteQty': '49.86276400', 'status': 'NEW', 'timeInForce': 'FOK', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': epoch_format, 'updateTime': 1622783728327, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        with self.assertRaises(BinanceAPIException):
            self.market_object.asset_object.has_active_orders()
        
    def test_unsold_orders_1(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693373, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22370000', 'origQty': '81.46000000', 'executedQty': '81.46000000', 'cummulativeQuoteQty': '99.68260200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886438499, 'updateTime': 1622886445108, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693590, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22690000', 'origQty': '40.75000000', 'executedQty': '40.75000000', 'cummulativeQuoteQty': '49.98802500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886472913, 'updateTime': 1622886472913, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.assertTrue(len(self.market_object.asset_object.get_unsold_orders()) == 1)

    def test_unsold_orders_2(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693373, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22370000', 'origQty': '81.46000000', 'executedQty': '81.46000000', 'cummulativeQuoteQty': '99.68260200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886438499, 'updateTime': 1622886445108, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693590, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22690000', 'origQty': '40.75000000', 'executedQty': '40.75000000', 'cummulativeQuoteQty': '49.98802500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886472913, 'updateTime': 1622886472913, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.assertTrue(len(self.market_object.asset_object.get_unsold_orders()) == 2)

    def test_unsold_orders_3(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693373, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22370000', 'origQty': '81.46000000', 'executedQty': '81.46000000', 'cummulativeQuoteQty': '99.68260200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886438499, 'updateTime': 1622886445108, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693590, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22690000', 'origQty': '40.75000000', 'executedQty': '40.75000000', 'cummulativeQuoteQty': '49.98802500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886472913, 'updateTime': 1622886472913, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.assertTrue(len(self.market_object.asset_object.get_unsold_orders()) == 4)

    def test_unsold_orders_4(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'CANCELLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693373, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22370000', 'origQty': '81.46000000', 'executedQty': '81.46000000', 'cummulativeQuoteQty': '99.68260200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886438499, 'updateTime': 1622886445108, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693590, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22690000', 'origQty': '40.75000000', 'executedQty': '40.75000000', 'cummulativeQuoteQty': '49.98802500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886472913, 'updateTime': 1622886472913, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.22620000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'CANCELLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.assertTrue(len(self.market_object.asset_object.get_unsold_orders()) == 4)

    def test_double_down_1(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.price = 0.97
        self.market_object.asset_object.gbp_price = 0.97
        self.market_object.asset_object.avaiable_cash = 51
        
        # Verifies that that it will double down
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(50) == 51.55)
        self.market_object.asset_object.purchase_amount = 51.55
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertTrue(self.market_object.is_buy_time())
        self.assertTrue(self.market_object.double_down())

    def test_double_down_2(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.market_object.asset_object.price = 0.9799
        self.market_object.asset_object.gbp_price = 0.9799
        self.market_object.asset_object.avaiable_cash = 49
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.asset_holdings = 100

        # Won't buy due to insufficent cash
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(50) == 51.03)
        self.market_object.asset_object.purchase_amount = 51.03
        self.assertFalse(self.market_object.asset_object.enough_avaiable_cash())
        self.assertFalse(self.market_object.is_buy_time())
        self.assertFalse(self.market_object.double_down())

    def test_double_down_3(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.98000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.market_object.asset_object.price = 0.97
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.gbp_price = 0.97
        self.market_object.asset_object.avaiable_cash = 51
        self.market_object.asset_object.asset_holdings = 100
        
        # Won't buy due to lack of price descrease
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(50) == 51.55)
        self.market_object.asset_object.purchase_amount = 51.55
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertFalse(self.market_object.is_buy_time())
        self.assertFalse(self.market_object.double_down())

    def test_double_down_4(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.97990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.market_object.asset_object.price = 0.9599
        self.market_object.asset_object.gbp_price = 0.9599
        self.market_object.asset_object.avaiable_cash = 51
        self.market_object.asset_object.asset_holdings = 100
        self.market_object.asset_object.quantity_precision = 0.01
        
        # Will buy because of enough price decrease
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(50) == 52.09)
        self.market_object.asset_object.purchase_amount = 52.09
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertTrue(self.market_object.is_buy_time())
        self.assertTrue(self.market_object.double_down())

    def test_double_down_5(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.95990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.91990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.market_object.asset_object.price = 0.879
        self.market_object.asset_object.gbp_price = 0.879
        self.market_object.asset_object.avaiable_cash = 50
        self.market_object.asset_object.asset_holdings = 100
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.purchase_amount = 50
        

        # Will buy because of enough price descrase
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(50) == 56.88)
        self.market_object.asset_object.purchase_amount = 56.88
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertTrue(self.market_object.is_buy_time())
        self.assertTrue(self.market_object.double_down())

    def test_double_down_6(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.98000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.96000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.94000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.92000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.90000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.88000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.market_object.asset_object.price = 0.87
        self.market_object.asset_object.gbp_price = 0.87
        self.market_object.asset_object.avaiable_cash = 51
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.asset_holdings = 100
        
        # Wont buy due to lack of price decrase
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(50) == 57.47)
        self.market_object.asset_object.purchase_amount = 57.47
        self.assertTrue(self.market_object.asset_object.enough_avaiable_cash())
        self.assertFalse(self.market_object.is_buy_time())
        self.assertFalse(self.market_object.double_down())

    def test_double_down_7(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.00000000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.98990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.97990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.96990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.95990000', 'origQty': '40.77000000', 'executedQty': '40.77000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.market_object.asset_object.price = 0.911
        self.market_object.asset_object.gbp_price = 0.911
        self.market_object.asset_object.asset_holdings = 100
        self.market_object.asset_object.quantity_precision = 0.01
        self.market_object.asset_object.avaiable_cash = 51

        # Won't buy to lack of price decrase
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(50) == 54.88)
        self.market_object.asset_object.purchase_amount = 54.88
        self.assertTrue(self.market_object.asset_object.get_asset_holding_worth() == 185.70735)
        self.assertTrue(self.market_object.asset_object.get_total_buy_quantity() == 203.85)
        self.assertFalse(self.market_object.is_buy_time())
        self.assertFalse(self.market_object.double_down())

    def test_asset_holding_worth(self):
        self.market_object.asset_object.price = 0.98
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.40000000', 'origQty': '40.77000000', 'executedQty': '23.0000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.assertTrue(self.market_object.asset_object.get_asset_holding_worth() == 22.54)
        
    def test_buy_asset(self):
        self.market_object.asset_object.price = 0.91
        self.market_object.asset_object.gbp_price = 0.91
        self.market_object.asset_object.quantity_precision = 0.1
        qty = self.market_object.asset_object.get_purchase_amount(50)
        self.market_object.asset_object.purchase_amount = qty
        order = self.market_object.asset_object.test_buy_asset()
        self.assertTrue(order["executedQty"] == 54.9 )
        self.assertTrue(order["price"] == 0.91 )

    def test_get_total_buy_in_amount_1(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.40000000', 'origQty': '40.77000000', 'executedQty': '40.2000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.30000000', 'origQty': '40.77000000', 'executedQty': '40.3000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693373, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.20000000', 'origQty': '81.46000000', 'executedQty': '40.1000000', 'cummulativeQuoteQty': '99.68260200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886438499, 'updateTime': 1622886445108, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693590, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.10000000', 'origQty': '40.75000000', 'executedQty': '40.3000000', 'cummulativeQuoteQty': '49.98802500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886472913, 'updateTime': 1622886472913, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.market_object.asset_object.price = 1.23
        
        self.assertTrue(self.market_object.asset_object.get_asset_holding_worth() == 197.907)
        self.assertTrue(self.market_object.asset_object.get_total_buy_quantity() == 160.9)
        self.assertTrue(self.market_object.asset_object.get_total_buy_in_amount() == 201.12)

    def test_get_total_buy_in_amount_2(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'ADAGBP', 'orderId': 19692858, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '4.0000000', 'origQty': '5.00000000', 'executedQty': '4.00000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886369535, 'updateTime': 1622886403711, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693066, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '3.0000000', 'origQty': '4.00000000', 'executedQty': '3.00000000', 'cummulativeQuoteQty': '49.99217400', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886404658, 'updateTime': 1622886405026, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693373, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '2.0000000', 'origQty': '11.00000000', 'executedQty': '2.00000000', 'cummulativeQuoteQty': '99.68260200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886438499, 'updateTime': 1622886445108, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'ADAGBP', 'orderId': 19693590, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '1.0000000', 'origQty': '5.00000000', 'executedQty': '1.00000000', 'cummulativeQuoteQty': '49.98802500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1622886472913, 'updateTime': 1622886472913, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
        ]
        self.market_object.asset_object.price = 0.89
        self.assertTrue(self.market_object.asset_object.get_asset_holding_worth() == 8.9)
        self.assertTrue(self.market_object.asset_object.get_total_buy_quantity() == 10)
        self.assertTrue(self.market_object.asset_object.get_total_buy_in_amount() == 30)

    def test_using_the_correct_buy_order(self):
        self.market_object.asset_object.orders = [
            {'symbol': 'BNBETH', 'orderId': 483624319, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.16333000', 'origQty': '0.25000000', 'executedQty': '0.25000000', 'cummulativeQuoteQty': '0.04084250', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1626417893487, 'updateTime': 1626417893487, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'BNBETH', 'orderId': 483625487, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.16331000', 'origQty': '0.50000000', 'executedQty': '0.50000000', 'cummulativeQuoteQty': '0.08165500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1626418065238, 'updateTime': 1626418082122, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'BNBETH', 'orderId': 485564877, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.15629000', 'origQty': '0.50000000', 'executedQty': '0.50000000', 'cummulativeQuoteQty': '0.07814500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1626709072453, 'updateTime': 1626709072520, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'BNBETH', 'orderId': 487340587, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.14820000', 'origQty': '0.05000000', 'executedQty': '0.05000000', 'cummulativeQuoteQty': '0.00741000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1626940972516, 'updateTime': 1626940978981, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'BNBETH', 'orderId': 487341125, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.14812000', 'origQty': '0.05000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'CANCELED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1626941031493, 'updateTime': 1626941220285, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'BNBETH', 'orderId': 487342653, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.14829000', 'origQty': '0.05000000', 'executedQty': '0.05000000', 'cummulativeQuoteQty': '0.00741450', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1626941222260, 'updateTime': 1626941224591, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
            {'symbol': 'BNBETH', 'orderId': 488182139, 'orderListId': -1, 'clientOrderId': 'crypto_bot_created11111', 'price': '0.14022000', 'origQty': '0.10000000', 'executedQty': '0.10000000', 'cummulativeQuoteQty': '0.01402200', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1627059137903, 'updateTime': 1627059140974, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'},
        ]
        self.market_object.asset_object.price = 0.14829
        self.market_object.asset_object.gbp_price = 215
        self.market_object.asset_object.avaiable_cash = 51
        self.market_object.asset_object.quantity_precision = 0.01

        # Make sure that the ordering of orders are correct
        unsold_orders = self.market_object.asset_object.get_unsold_orders()
        self.assertTrue(self.market_object.asset_object.get_purchase_amount(50) == 0.23)
        self.market_object.asset_object.purchase_amount = 0.23
        self.assertTrue(self.market_object.asset_object.get_asset_holding_worth() == 0.103803)
        self.assertTrue(self.market_object.asset_object.get_total_buy_quantity() == 0.7   )  
        self.assertFalse(self.market_object.is_sell_time()) 
        self.assertTrue(len(unsold_orders) == 4) 
        self.assertFalse(self.market_object.double_down())
        self.assertTrue(self.market_object.asset_object.get_purchase_price() == 0.15629)

        # Make sure that the the order to compare is the last in list 
        original_order_time = datetime.datetime.fromtimestamp(int(unsold_orders[-1]["time"]/1000))
        for order in unsold_orders[:-1]:
            order_time = datetime.datetime.fromtimestamp(int(order["time"]/1000))
            self.assertTrue(order_time > original_order_time)

        # Make sure that the the order to compare is the fist in list 
        orders = self.market_object.asset_object.orders
        original_order_time = datetime.datetime.fromtimestamp(int(orders[0]["time"]/1000))
        for order in orders[1:]:
            order_time = datetime.datetime.fromtimestamp(int(order["time"]/1000))
            self.assertTrue(order_time > original_order_time)

if __name__ == '__main__':
    unittest.main()