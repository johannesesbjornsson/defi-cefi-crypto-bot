import os
import json
import sys
import datetime
from binance.helpers import round_step_size
import plotting

sys.path.append('../../application')
import binance_client
import binance_market_client
import application_config as cfg


def get_dataset(dataset):
    with open(dataset+'.json') as f:
        d = json.load(f)
    return d

def get_average_price(data):
    total_price = 0.00 
    for entry in data:
        total_price += float(entry[4])

    average_price = total_price / len(data)
    return average_price

def get_price(entry):    
    return float(entry[4])


def set_market_conditions(market_object,i,dataset,entry):
    market_object.average_price_last_week = get_average_price(dataset[i-180:i])
    market_object.average_price_last_hours = get_average_price(dataset[i-180:i])
    market_object.average_price_last_period = get_average_price(dataset[i-10:i])
    market_object.asset_object.price = get_price(entry)
    market_object.asset_object.gbp_price = get_price(entry)
    return market_object


def set_ema_market_conditions(market_object,i,dataset,entry):
    market_object.asset_object.price = get_price(entry)
    market_object.asset_object.gbp_price = get_price(entry)

    market_object.market_data = dataset[i-180:i]
    #if btc_dataset is not None: 
    #    market_object.btc_market_data = btc_dataset[i-50:i]
    market_object.calculate_ema()

    return market_object

def main(dataset,market_object,avaiable_cash=1500,gbp_purchase_amount=50):
    total_profits = 0
    dates = []
    values = []
    volume = []
    trading_volume = 0
    action_dates = []
    market_object.asset_object.asset_holdings = 0
    market_object.asset_object.avaiable_cash = avaiable_cash
    market_object.asset_object.orders = []
    for i in range(180,len(dataset)):
        entry = dataset[i]
        timestamp = datetime.datetime.fromtimestamp(int(entry[0]/1000)).strftime('%c')
        order = None
        order_profit = 0

        #market_object = set_market_conditions(market_object,i,dataset,entry) 
        market_object = set_ema_market_conditions(market_object,i,dataset,entry) 

        time_to_sell = market_object.is_sell_time() 
        if time_to_sell:
            order = market_object.asset_object.test_sell_asset()
            order_profit = (market_object.asset_object.asset_holdings * market_object.asset_object.price ) - market_object.asset_object.get_total_buy_in_amount()
            total_profits =  total_profits + order_profit
        else:
            time_to_buy = market_object.is_buy_time()
            if time_to_buy:
                market_object.asset_object.purchase_amount = market_object.asset_object.get_purchase_amount(gbp_purchase_amount)
                order = market_object.asset_object.test_buy_asset()


        if order is not None:
            if order["side"] == "SELL":
                market_object.asset_object.avaiable_cash = market_object.asset_object.avaiable_cash + (market_object.asset_object.asset_holdings * market_object.asset_object.price )
                market_object.asset_object.asset_holdings = 0
            elif order["side"] == "BUY":
                market_object.asset_object.asset_holdings = market_object.asset_object.asset_holdings + order["executedQty"]
                market_object.asset_object.avaiable_cash = market_object.asset_object.avaiable_cash - (order["executedQty"] * market_object.asset_object.price )

            market_object.asset_object.orders.append(order)
            action_dates.append({
                "action": order["side"],
                "price": order["price"],
                "executedQty": order["executedQty"],
                "date": timestamp,
                "avaiable_cash": market_object.asset_object.avaiable_cash,
                "order_profit": order_profit,
            })
            trading_volume = trading_volume + (order["executedQty"] * order["price"])





        dates.append(timestamp)
        values.append(market_object.asset_object.price)
        #if btc_dataset is not None:
        #    btc_values.append(get_price(btc_dataset[i]))
        #volume.append(float(entry[5]))

    postion_worth = market_object.asset_object.asset_holdings * market_object.asset_object.price
    return dates, \
        values, \
        action_dates, \
        trading_volume, \
        round_step_size(total_profits, 0.00001), \
        round_step_size(market_object.asset_object.avaiable_cash, 0.00001), \
        round_step_size(postion_worth, 0.00001)



if __name__ == '__main__':
    starting_cash = 1500
    currency = "ETH"
    purchase_amount = 50
    dataset = get_dataset("dataset")
    #btc_dataset = None #get_dataset("btc_dataset")

    client = binance_client.get_client(cfg.api_key,cfg.api_secret)
    asset_object = binance_client.Asset(client,currency, purchase_amount=purchase_amount)            
    #market_object = binance_market_client.Market(asset_object)
    market_object = binance_market_client.EMAMarket(asset_object)
    


    dates, values, action_dates, trading_volume, total_profits, avaiable_cash, postion_worth = main(dataset,market_object,starting_cash,purchase_amount)
    #fig = plotting.get_figure(dates, values, action_dates, total_profits, avaiable_cash, postion_worth, starting_cash,asset_object.asset)
    #fig.show()

    
    import pandas as pd
    import numpy as np

    df = pd.DataFrame(data = values)
    df_ema = df.ewm(span=3).mean()
    df_ema_medium = df.ewm(span=6).mean()
    df_ema_long = df.ewm(span=9).mean()
    #df_ma = df.rolling(window=5).mean()
    #ma_list = df_ma[0].tolist()

    ema_list = df_ema[0].tolist()
    ema_medium = df_ema_medium[0].tolist()
    ema_long = df_ema_long[0].tolist()
    

    fig = plotting.get_figure(dates, values, ema_list, ema_medium, ema_long, action_dates, trading_volume, total_profits, avaiable_cash, postion_worth, starting_cash,asset_object.asset)
    fig.show()



    


