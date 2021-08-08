from binance.client import Client
import math
from binance.enums import *
from binance.helpers import round_step_size
import datetime
from binance.exceptions import BinanceAPIException
from binance_client import Asset

class Market(Asset):

    def __init__(self, asset_object,number_of_double_downs=30, short_time_compare_mins=10, medium_time_compare_hours=3):
        if type(asset_object) != Asset:
            raise ValueError("Argument must be object type Asset")
        self.symbol = asset_object.symbol
        self.client = asset_object.client
        self.asset_object = asset_object
        self.average_price_medium_period = None
        self.number_of_double_downs = number_of_double_downs
        self.average_price_short_period = None
        self.average_price_last_week = None
        self.short_time_compare_mins = short_time_compare_mins
        self.medium_time_compare_hours = str(medium_time_compare_hours)

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
        last_hours_data = self.client.get_historical_klines(self.symbol, '1m', self.medium_time_compare_hours+" hours ago GMT")
        last_weeks_data = self.client.get_historical_klines(self.symbol, '1h', "7 days ago GMT")
        
        self.average_price_last_hours = self.get_average_price(last_hours_data)
        self.average_price_last_period = self.get_average_price(last_hours_data[-self.short_time_compare_mins:])
        self.average_price_last_week = self.get_average_price(last_weeks_data)

    def market_good_for_buying(self):
        is_buy_time = False
        market_too_hot = True
        high_compared_to_last_week = True
        price_to_high_last_period = True
        
        if (self.asset_object.price/self.average_price_last_hours) < 0.98:
            market_too_hot = False        
        if (self.average_price_last_hours/self.average_price_last_week) <= 1:
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
            is_buy_time = self.double_down()
        
        elif enough_avaiable_cash:
            is_buy_time = self.market_good_for_buying()
        return is_buy_time

    def double_down(self):
        double_down = False
        price_to_compare = self.asset_object.get_purchase_price()
        unsold_orders = len(self.asset_object.get_unsold_orders())
        if self.asset_object.enough_avaiable_cash() and self.number_of_double_downs > unsold_orders:
            price_threshold = (100 - unsold_orders * 2) * 0.01
            if (self.asset_object.price / price_to_compare) < price_threshold:
                double_down = True

        return double_down

    def is_sell_time(self):
        is_sell_time = False
        unsold_orders = self.asset_object.get_unsold_orders()

        if len(unsold_orders) > 0: 
            price_to_compare = self.asset_object.get_purchase_price()
            if (self.asset_object.price / price_to_compare) > 1.03:
                is_sell_time = True
            elif (self.asset_object.get_asset_holding_worth() / self.asset_object.get_total_buy_in_amount()) > 1.1 :
                is_sell_time = True

        return is_sell_time




class EMAMarket(Asset):

    def __init__(self, asset_object):
        if type(asset_object) != Asset:
            raise ValueError("Argument must be object type Asset")
        self.symbol = asset_object.symbol
        self.client = asset_object.client
        self.asset_object = asset_object
        self.market_data


    def set_market_data(self):
        market_data = self.client.get_historical_klines(self.symbol, '5m', "15 hours ago GMT")
        data = []
        for entry in market_data:
            data.append(entry[4])

        self.market_data = data

    def calculate_ema(self):
        import pandas as pd
        import numpy as np

        df = pd.DataFrame(data = self.market_data)
        df_ema = df.ewm(span=3).mean()
        df_ema_medium = df.ewm(span=6).mean()
        df_ema_long = df.ewm(span=9).mean()
        #df_ma = df.rolling(window=5).mean()
        #ma_list = df_ma[0].tolist()

        ema_list = df_ema[0].tolist()
        ema_medium = df_ema_medium[0].tolist()
        ema_long = df_ema_long[0].tolist()
