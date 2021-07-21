from binance.client import Client
import math
from binance.enums import *
from binance.helpers import round_step_size
import datetime
from binance.exceptions import BinanceAPIException

class Asset(object):

    def __init__(self, client, asset, precision=6, purchase_amount=50, currency="GBP",number_of_double_downs=30):
        self.client = client
        self.asset = asset
        self.currency = currency
        self.symbol = asset+currency
        self.precision = precision
        self.number_of_double_downs = number_of_double_downs
        self.purchase_amount = purchase_amount
        self.avaiable_cash = self.get_asset_amount(currency)
        self.asset_holdings = self.get_asset_amount(asset)
        self.update_price()
        self.update_orders()

    def update_price(self):
        current_price = self.client.get_symbol_ticker(symbol=self.symbol).get("price")
        self.price = float(current_price)

    def update_orders(self):
        orders = self.client.get_all_orders(symbol=self.symbol, limit=40)
        self.orders = orders

    def get_asset_amount(self, asset):
        balance = float(self.client.get_asset_balance(asset=asset).get("free"))
        return balance

    def round_down(self, n):
        multiplier = 10 ** self.precision
        return math.floor(n * multiplier) / multiplier

    
    def has_active_orders(self):
        active_order_exist = False
        for order in self.orders:
            order_created = datetime.datetime.fromtimestamp(int(order["time"]/1000))
            oldest_allowed_order =  datetime.datetime.now()-datetime.timedelta(seconds=180)
            
            if order["status"] == "NEW":
                if order_created < oldest_allowed_order:
                    self.client.cancel_order(symbol=self.symbol,orderId=order["orderId"])
                else:
                    active_order_exist = True
        
        return active_order_exist

    def test_buy_asset(self):
        position_to_buy = self.purchase_amount

        order = self.client.create_test_order(
            symbol=self.symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=position_to_buy,
            price=self.price)
            
        return order

    def test_sell_asset(self):
        position_to_sell = self.get_total_buy_quantity()
        print(position_to_sell)

        order = self.client.create_test_order(
            symbol=self.symbol,
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=position_to_sell,
            price=self.price)

        return order

    def buy_asset(self):
        position_to_buy = self.purchase_amount

        order = self.client.create_order(
            symbol=self.symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=position_to_buy,
            price=self.price)
            
        return order

    def sell_asset(self):
        position_to_sell = self.get_total_buy_quantity()
        print(position_to_sell)

        order = self.client.create_order(
            symbol=self.symbol,
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=77, #position_to_sell,
            price=self.price)

        return order

    def get_unsold_orders(self):
        orders_not_sold = []
        for order in reversed(self.orders):
            if order["status"] != "FILLED":
                continue
            if order["side"] == "SELL":
                break
            orders_not_sold.append(order)
        return orders_not_sold

    def get_purchase_price(self):
        order_to_compare = self.get_unsold_orders()[-1]

        if order_to_compare["price"] != "0.00000000": 
            price_to_compare = float(order_to_compare["price"])
        else:
            price_to_compare = float(order_to_compare["cummulativeQuoteQty"]) / float(order_to_compare["executedQty"])
        return price_to_compare

    def is_sell_time(self):
        is_sell_time = False
        unsold_orders = self.get_unsold_orders()
        
        if len(unsold_orders) > 0: 
            price_to_compare = self.get_purchase_price()
            if (self.price / price_to_compare) > 1.03:
                is_sell_time = True
            elif (self.get_asset_holding_worth() / self.get_total_buy_in_amount()) > 1.1 :
                is_sell_time = True

        return is_sell_time

    def get_asset_holding_worth(self):
        asset_worth = self.get_total_buy_quantity() * self.price
        return round_step_size(asset_worth, 0.0000001 )

    def enough_avaiable_cash(self):
        enough_avaiable_cash = False
        if self.purchase_amount < self.avaiable_cash:
            enough_avaiable_cash = True
        return enough_avaiable_cash
            
    def double_down(self):
        double_down = False
        price_to_compare = self.get_purchase_price()
        unsold_orders = len(self.get_unsold_orders())
        if self.enough_avaiable_cash() and self.number_of_double_downs > unsold_orders:
            price_threshold = (100 - unsold_orders * 2) * 0.01
            if (self.price / price_to_compare) < price_threshold:
                double_down = True
            

        return double_down

    def get_total_buy_in_amount(self):
        unsold_orders = self.get_unsold_orders()
        total_buy_in_amount = 0.00
        for order in unsold_orders:
            total_buy_in_amount = total_buy_in_amount + ( float(order["price"]) *  float(order["executedQty"]) )

        return round_step_size(total_buy_in_amount, 0.0000001 )

    def get_total_buy_quantity(self):
        unsold_orders = self.get_unsold_orders()
        total_quantity = 0.00
        for order in unsold_orders:
            total_quantity = total_quantity + float(order["executedQty"])

        return round_step_size(total_quantity, 0.0000001 )

class Market(Asset):

    def __init__(self, asset_object, holding_threshold=20):
        if type(asset_object) != Asset:
            raise ValueError("Argument must be object type Asset")
        self.symbol = asset_object.symbol
        self.client = asset_object.client
        self.asset_object = asset_object
        self.average_price_thee_hour = None
        self.average_price_last_period = None
        self.average_price_last_week = None
        self.holding_threshold = holding_threshold

    def get_average_price(self,data):
        total_price = 0.00 
        for entry in data:
            total_price += float(entry[4])
        #    timestamp = datetime.datetime.fromtimestamp(int(entry[0]/1000)).strftime('%c')
        #    print(timestamp, entry[4])
        #print("---")

        average_price = round_step_size (total_price / len(data), 0.000001 )
        return average_price
        

    def set_market_data(self):
        last_hours_data = self.client.get_historical_klines(self.symbol, '1m', "3 hours ago GMT")
        last_weeks_data = self.client.get_historical_klines(self.symbol, '1h', "7 days ago GMT")
        
        self.average_price_thee_hour = self.get_average_price(last_hours_data)
        self.average_price_last_period = self.get_average_price(last_hours_data[-10:])
        self.average_price_last_week = self.get_average_price(last_weeks_data)

    def market_good_for_buying(self):
        is_buy_time = False
        market_too_hot = True
        high_compared_to_last_week = True
        price_to_high_last_period = True
        
        if (self.asset_object.price/self.average_price_thee_hour) < 0.98:
            market_too_hot = False        
        if (self.average_price_thee_hour/self.average_price_last_week) < 1.06:
            high_compared_to_last_week = False
        if self.asset_object.price/self.average_price_last_period < 0.995:
            price_to_high_last_period = False

        if price_to_high_last_period == False and high_compared_to_last_week == False and market_too_hot == False:
            is_buy_time = True

        return is_buy_time



    def is_buy_time(self):
        is_buy_time = False
        enough_avaiable_cash = self.asset_object.enough_avaiable_cash()
        unsold_orders = self.asset_object.get_unsold_orders()
        if enough_avaiable_cash and len(unsold_orders) > 0:
            is_buy_time = self.asset_object.double_down()
        
        elif enough_avaiable_cash:
            is_buy_time = self.market_good_for_buying()


        return is_buy_time


def get_client(api_key,api_secret):
    client = Client(api_key, api_secret)
    return client

#@catch_exception
#
#def catch_exception(f):
#    @functools.wraps(f)
#    def func(*args, **kwargs):
#        try:
#            return f(*args, **kwargs)
#        except Exception as e:
#            print('Caught an exception in', f.__name__)
#    return func