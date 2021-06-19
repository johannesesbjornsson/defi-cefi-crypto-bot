import os
import json
import sys
import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go

sys.path.append('../application')
import binance_client
import application_config as cfg


def get_dataset():
    with open('dataset.json') as f:
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


def get_figure(dates, values, action_dates, total_profits, avaiable_cash, postion_worth):
    fig = go.Figure(data=[go.Scatter(x=dates, y=values)])
    
    fig.update_layout(
        title_text="Total sales profits: "+ str(total_profits)+" <br>Avaiable cash: " +str(avaiable_cash)+" <br>Portfolio worth: " +str( avaiable_cash+ postion_worth)
    )
    for action in action_dates:
        if action["action"] == "BUY":
            color = "#ff7f0e"
        else: 
            color = "#00FF00"
    
        fig.add_annotation(
            x=action["date"],
            y=action["price"],
            xref="x",
            yref="y",
            arrowcolor=color,
            showarrow=True,
            borderwidth=0.1,
            borderpad=0.1,
            arrowwidth=1,
            arrowhead=1,
            ay=-80,
            ax=-10,
            bgcolor=color,
            )
    return fig


def main(dataset,market_object,avaiable_cash=1500):
    orders = []
    total_profits = 0
    dates = []
    values = []
    action_dates = []
    market_object.asset_object.avaiable_cash = avaiable_cash
    for i in range(180,len(dataset)):
        entry = dataset[i]
        timestamp = datetime.datetime.fromtimestamp(int(entry[0]/1000)).strftime('%c')
        order = None


        market_object.average_price_last_week = get_average_price(dataset[i-180:i])
        market_object.average_price_thee_hour = get_average_price(dataset[i-180:i])
        market_object.average_price_last_period = get_average_price(dataset[i-10:i])
        
        market_object.asset_object.price = get_price(entry)

        dates.append(timestamp)
        values.append(market_object.asset_object.price)

        time_to_sell = market_object.asset_object.is_sell_time() 
        if time_to_sell:
            order = {"status" : "FILLED", 'side': 'SELL', 'price': market_object.asset_object.price, "executedQty" : market_object.asset_object.asset_holdings }
            total_profits =  total_profits + ((market_object.asset_object.asset_holdings * asset_object.price ) - asset_object.get_total_buy_in_amount())
            market_object.asset_object.avaiable_cash = market_object.asset_object.avaiable_cash + (market_object.asset_object.asset_holdings * asset_object.price )
            market_object.asset_object.asset_holdings = 0
            print("sell", market_object.asset_object.avaiable_cash)
        else:
            time_to_buy = market_object.is_buy_time()
            if time_to_buy:
                position = market_object.asset_object.purchase_amount / market_object.asset_object.price
                order = {"status" : "FILLED", 'side': 'BUY', 'price': market_object.asset_object.price, "executedQty" : position }
                market_object.asset_object.asset_holdings = market_object.asset_object.asset_holdings + order["executedQty"]
                market_object.asset_object.avaiable_cash = market_object.asset_object.avaiable_cash - (position * asset_object.price )
                print("buy", market_object.asset_object.avaiable_cash)
                


        if order is not None:
            timestamp = datetime.datetime.fromtimestamp(int(entry[0]/1000)).strftime('%c')

            asset_object.orders.append(order)
            action_dates.append({
                "action": order["side"],
                "price": order["price"],
                "date": timestamp
            })

    postion_worth = market_object.asset_object.asset_holdings * asset_object.price
    return dates, values, action_dates, total_profits, market_object.asset_object.avaiable_cash, postion_worth



if __name__ == '__main__':
    starting_cash = 1500
    currency = "BTC"
    purchase_amount = 50
    precision = 6

    client = binance_client.get_client(cfg.api_key,cfg.api_secret)
    asset_object = binance_client.Asset(client,currency, precision=precision, purchase_amount=purchase_amount)
    market_object = binance_client.Market(asset_object)
    dataset = get_dataset()

    dates, values, action_dates, total_profits, avaiable_cash, postion_worth = main(dataset,market_object,starting_cash)

    fig = get_figure(dates, values, action_dates, total_profits, avaiable_cash, postion_worth)

    fig.show()