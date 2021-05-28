import logic
import binance_client
import logging
import test
import time

current_holdings = {}
buy_amount = 50
assets_to_check = [
    "BTC",
    "ETH",
    "XRP"
]


def look_to_buy(client,asset,current_price,last_hours_data=None,last_weeks_data=None,for_real=True):
    is_buy_time = False
    if for_real:
        last_hours_data = binance_client.get_last_hours_of_data(client,asset)
        last_weeks_data = binance_client.get_last_weeks_of_data(client,asset)

    market_good, average_price_last_period = logic.get_maket_status(last_hours_data,last_weeks_data)

    if market_good:
        is_buy_time = logic.is_buy_time(average_price_last_period,current_price)
    
    if is_buy_time:
        order = binance_client.buy_asset(client,asset,buy_amount)
        print(order)



def look_to_sell(client,asset,current_price,asset_amount):
    time_to_sell = logic.is_sell_time(current_price, asset_amount, buy_amount)

    if time_to_sell:
        order = binance_client.sell_asset(client,asset,asset_amount)
        print(order)
    

def main(client):
    for asset in assets_to_check:
        asset_amount = binance_client.get_asset_amount(client, asset)
        current_price = binance_client.get_price(client,asset)
        
        if (asset_amount * current_price) > 20:
            print("Already have "+asset+", looking to sell")

            look_to_sell(client,asset,current_price,asset_amount)
        else:
            print("Don't have "+asset+", looking to buy")
            look_to_buy(client,asset,current_price)






#hours = test.get_test_set_hours()
client = binance_client.get_client()
while True:
    #depth = client.get_order_book(symbol='BTCGBP', limit=5000)
    #current_price = float(client.get_symbol_ticker(symbol="BTCGBP").get("price"))
    #total_bids = 0.00
    #for trade in depth["bids"]:
    #    total_bids += float(trade[0])
    #    
    #
    print("---")
    #for trade in depth["asks"]:
    #    ask_evalutation = float(trade[0]) / float(trade[1])
    #    if ask_evalutation > current_price:
    #        print(ask_evalutation)
    #print(total_bids)
    #print(current_price)
    #print(len(depth["asks"]))
    #print(len(depth["bids"]))
    main(client)
    time.sleep(30)