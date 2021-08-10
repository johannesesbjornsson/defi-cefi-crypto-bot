from binance.client import Client
import math
from binance.enums import *
from binance.helpers import round_step_size
import datetime
from binance.exceptions import BinanceAPIException

class Asset(object):

    def __init__(self, client, asset, purchase_amount=50, currency="GBP"):
        self.client = client
        self.asset = asset
        self.currency = currency
        self.symbol = asset+currency
        self.update_price()
        self.gbp_price = self.get_gbp_price()
        self.quantity_precision = self.get_quantity_precision()
        self.purchase_amount = self.get_purchase_amount(purchase_amount)
        self.avaiable_cash = self.get_asset_amount(currency)
        self.asset_holdings = self.get_asset_amount(asset)
        self.update_orders()
        

    def get_quantity_precision(self):
        exhange_info = self.client.get_exchange_info()
        for symbol in exhange_info["symbols"]:
            if symbol["symbol"] == self.symbol:
                lot_size = dict(("lot_size", item["stepSize"]) for item in symbol["filters"] if item["filterType"] == "LOT_SIZE")["lot_size"]

        return float(lot_size)

    def get_gbp_price(self):
        gbp_price = self.client.get_symbol_ticker(symbol=self.asset+"GBP").get("price")
        return float(gbp_price)

    def get_purchase_amount(self,purchase_amount_in_gbp):
        quantity = purchase_amount_in_gbp / self.gbp_price
        precise_quantity = round_step_size(quantity, self.quantity_precision )

        return precise_quantity

        

    def update_price(self):
        current_price = self.client.get_symbol_ticker(symbol=self.symbol).get("price")
        self.price = float(current_price)

    def update_orders(self):
        orders = self.client.get_all_orders(symbol=self.symbol, limit=40)
        self.orders = orders

    def get_asset_amount(self, asset):
        balance = float(self.client.get_asset_balance(asset=asset).get("free"))
        return balance
    
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

    def generate_timestamp(self):
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return now

    def test_buy_asset(self):
        position_to_buy = self.purchase_amount
        order_id = "crypto_bot_created"+self.generate_timestamp()

        order = self.client.create_test_order(
            symbol=self.symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            newClientOrderId=order_id,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=position_to_buy,
            price="{:.8f}".format(self.price))

        order = {
            "status" : "FILLED", 
            'side': 'BUY', 
            'newClientOrderId': order_id,
            'price': self.price, 
            "executedQty" : position_to_buy }
            
        return order

    def test_sell_asset(self):
        position_to_sell = self.get_total_buy_quantity()
        order_id = "crypto_bot_created"+self.generate_timestamp()

        order = self.client.create_test_order(
            symbol=self.symbol,
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            newClientOrderId=order_id,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=position_to_sell,
            price="{:.8f}".format(self.price))

        order = {
            "status" : "FILLED", 
            'side': 'SELL', 
            'newClientOrderId': order_id,
            'price': self.price, 
            "executedQty" : position_to_sell 
        }
        
        return order

    def buy_asset(self):
        position_to_buy = self.purchase_amount
        order_id = "crypto_bot_created"+self.generate_timestamp()

        order = self.client.create_order(
            symbol=self.symbol,
            side=SIDE_BUY,
            newClientOrderId=order_id,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=position_to_buy,
            price="{:.8f}".format(self.price))
            
        return order

    def sell_asset(self):
        position_to_sell = self.get_total_buy_quantity()
        order_id = "crypto_bot_created"+self.generate_timestamp()

        order = self.client.create_order(
            symbol=self.symbol,
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            newClientOrderId=order_id,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=position_to_sell,
            price="{:.8f}".format(self.price))

        return order

    def get_unsold_orders(self):
        orders_not_sold = []
        for order in reversed(self.orders):
            if not order["clientOrderId"].startswith('crypto_bot_created'):
                continue
            if order["status"] != "FILLED" and order["status"] != "PARTIALLY_FILLED":
                continue
            if order["status"] == "FILLED" and order["side"] == "SELL":
                break
            orders_not_sold.append(order)
        return orders_not_sold

    def get_purchase_price(self):
        #order_to_compare = self.get_unsold_orders()[-1]
        unsold_orders = self.get_unsold_orders()
        order_to_compare = {}
        for order in reversed(unsold_orders):
            if order["status"] == "FILLED":
                order_to_compare = order
                break

        if order_to_compare["price"] != "0.00000000":
            price_to_compare = float(order_to_compare["price"])
        else:
            price_to_compare = float(order_to_compare["cummulativeQuoteQty"]) / float(order_to_compare["executedQty"])
        return price_to_compare

    def get_asset_holding_worth(self):
        asset_worth = self.get_total_buy_quantity() * self.price
        return round_step_size(asset_worth, 0.0000001 )

    def enough_avaiable_cash(self):
        enough_avaiable_cash = False
        purchase_amount_required = self.purchase_amount * self.price

        if purchase_amount_required < self.avaiable_cash:
            enough_avaiable_cash = True
        return enough_avaiable_cash

    def get_total_buy_in_amount(self):
        unsold_orders = self.get_unsold_orders()
        total_buy_in_amount = 0.00
        for order in unsold_orders:
            if order["side"] == "BUY":
                total_buy_in_amount = total_buy_in_amount + ( float(order["price"]) *  float(order["executedQty"]) )
            elif order["side"] == "SELL":
                total_buy_in_amount = total_buy_in_amount - ( float(order["price"]) *  float(order["executedQty"]) )

        return round_step_size(total_buy_in_amount, 0.0000001 )

    def get_total_buy_quantity(self):
        unsold_orders = self.get_unsold_orders()
        total_quantity = 0.00
        for order in unsold_orders:
            if order["side"] == "BUY":
                total_quantity = total_quantity + float(order["executedQty"])
            elif order["side"] == "SELL":
                total_quantity = total_quantity - float(order["executedQty"])

        return round_step_size(total_quantity, 0.0000001 )


def get_client(api_key,api_secret):
    client = Client(api_key, api_secret)
    return client
