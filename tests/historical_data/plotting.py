import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_figure(dates, values, ema_values, ema_values_medium, ema_values_long, action_dates, trading_volume, total_profits, avaiable_cash, postion_worth, starting_cash,asset):
    fig = make_subplots(rows=2, cols=1,
                shared_xaxes=False,
                vertical_spacing=0.2,
                specs=[[{"type": "scatter"}],
                #specs=[[{"secondary_y": True}],
                    [{"type": "table"}]
                ]
           )

    trace1 = go.Scatter(x=dates, y=values,name="Price")
    trace2 = go.Scatter(x=dates, y=ema_values,name="EMA")
    trace3 = go.Scatter(x=dates, y=ema_values_medium,name="Medium EMA")
    trace4 = go.Scatter(x=dates, y=ema_values_long,name="Long EMA")
    #bars = go.Bar(x=dates, y=volume,name="Volume")
    
    fig.add_trace(trace1,row=1, col=1)
    fig.add_trace(trace2,row=1, col=1)
    fig.add_trace(trace3,row=1, col=1)
    fig.add_trace(trace4,row=1, col=1)
    #fig.add_trace(bars,row=1, col=1, secondary_y=True)
    
    
    fig.update_layout(
        title_text="<b>"+asset+"</b>"+
        "<br>Total sales profits: "+ str(total_profits)+
        "<br>Starting cash:" + str(starting_cash) + "          "+
        "Portfolio worth: " +str( avaiable_cash+ postion_worth) + "          "+
        "Trading Volume: " + str(trading_volume)
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

