import os
import json
import sys
import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


sys.path.append('../../application')
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


def get_figure(dates, values, action_dates, total_profits, avaiable_cash, postion_worth, starting_cash,asset):
    fig = make_subplots(rows=2, cols=1,
                shared_xaxes=False,
                vertical_spacing=0.2,
                specs=[[{"type": "scatter"}],
                    [{"type": "table"}]
                ]
           )
    
    trace1 = go.Scatter(x=dates, y=values)
    fig.add_trace(trace1,row=1, col=1)
    
    fig.update_layout(
        title_text="<b>"+asset+"</b>"+
        "<br>Total sales profits: "+ str(total_profits)+
        "<br>Starting cash:" + str(starting_cash) + "          "+
        "Portfolio worth: " +str( avaiable_cash+ postion_worth) 
        
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

    cells = [[],[],[],[],[]]
    colors = [] 
    for action in action_dates:
        cells[0].append(action["action"])
        cells[1].append(action["date"])
        cells[2].append(action["price"])
        cells[4].append(action["avaiable_cash"])
        
        if action["action"] == "BUY":
            cells[3].append("N/A")
            colors.append("orange")
        elif action["action"] == "SELL":
            cells[3].append(action["order_profit"]) 
            colors.append("lightgreen")            


    fig.add_trace(
        go.Table(
        header=dict(
            values=["Action","Date","Price", "Sales Profits", "Avaiable cash"],
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            fill_color=[colors],
            values=cells,
            align = "left")
    ),
    row=2, col=1)

    fig['layout'].update(height=1500)
    return fig


def main(dataset,market_object,avaiable_cash=1500):
    orders = []
    total_profits = 0
    dates = []
    values = []
    action_dates = []
    market_object.asset_object.asset_holdings = 0
    market_object.asset_object.avaiable_cash = avaiable_cash
    market_object.asset_object.orders = []
    for i in range(180,len(dataset)):
        entry = dataset[i]
        timestamp = datetime.datetime.fromtimestamp(int(entry[0]/1000)).strftime('%c')
        order = None
        order_profit = 0


        market_object.average_price_last_week = get_average_price(dataset[i-180:i])
        market_object.average_price_last_hours = get_average_price(dataset[i-180:i])
        market_object.average_price_last_period = get_average_price(dataset[i-10:i])
        
        market_object.asset_object.price = get_price(entry)

        dates.append(timestamp)
        values.append(market_object.asset_object.price)

        time_to_sell = market_object.asset_object.is_sell_time() 
        if time_to_sell:
            order = {"status" : "FILLED", 'side': 'SELL', 'price': market_object.asset_object.price, "executedQty" : market_object.asset_object.asset_holdings }
            order_profit = (market_object.asset_object.asset_holdings * market_object.asset_object.price ) - market_object.asset_object.get_total_buy_in_amount()
            total_profits =  total_profits + order_profit
            market_object.asset_object.avaiable_cash = market_object.asset_object.avaiable_cash + (market_object.asset_object.asset_holdings * market_object.asset_object.price )
            market_object.asset_object.asset_holdings = 0
        else:
            time_to_buy = market_object.is_buy_time()
            if time_to_buy:
                position = market_object.asset_object.purchase_amount #market_object.asset_object.purchase_amount / market_object.asset_object.price
                order = {"status" : "FILLED", 'side': 'BUY', 'price': market_object.asset_object.price, "executedQty" : position }
                market_object.asset_object.asset_holdings = market_object.asset_object.asset_holdings + order["executedQty"]
                market_object.asset_object.avaiable_cash = market_object.asset_object.avaiable_cash - (position * market_object.asset_object.price )
                


        if order is not None:
            timestamp = datetime.datetime.fromtimestamp(int(entry[0]/1000)).strftime('%c')

            market_object.asset_object.orders.append(order)
            action_dates.append({
                "action": order["side"],
                "price": order["price"],
                "executedQty": order["executedQty"],
                "date": timestamp,
                "avaiable_cash": market_object.asset_object.avaiable_cash,
                "order_profit": order_profit,
            })
        #if len(action_dates) > 2:
        #    break

    postion_worth = market_object.asset_object.asset_holdings * market_object.asset_object.price
    return dates, values, action_dates, total_profits, market_object.asset_object.avaiable_cash, postion_worth



if __name__ == '__main__':
    starting_cash = 1500
    currency = "BTC"
    purchase_amount = 0.005
    precision = 6

    client = binance_client.get_client(cfg.api_key,cfg.api_secret)
    asset_object = binance_client.Asset(client,currency, precision=precision, purchase_amount=purchase_amount)            
    market_object = binance_client.Market(asset_object)
    dataset = get_dataset()

    dates, values, action_dates, total_profits, avaiable_cash, postion_worth = main(dataset,market_object,starting_cash)

    fig = get_figure(dates, values, action_dates, total_profits, avaiable_cash, postion_worth, starting_cash,asset_object.asset)

    fig.show()