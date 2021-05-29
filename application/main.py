import logic
import binance_client
import logging
import time
import traceback

current_holdings = {}
buy_amount = 50
assets_to_check = [
    "BTC",
    "ETH",
    "XRP"
]


def look_to_buy(client,asset,current_price,last_hours_data=None,last_weeks_data=None,for_real=True):
    is_buy_time = False
    order = None

    if for_real:
        last_hours_data = binance_client.get_last_hours_of_data(client,asset)
        last_weeks_data = binance_client.get_last_weeks_of_data(client,asset)

    market_good, average_price_last_period = logic.get_maket_status(last_hours_data,last_weeks_data)

    if market_good:
        is_buy_time = logic.is_buy_time(average_price_last_period,current_price)
    
    if is_buy_time and for_real:
        current_price = binance_client.get_price(client,asset)
        order = binance_client.buy_asset(client,asset,buy_amount,current_price)
        logic.send_email_update("I bought some "+asset+" for you!")
    elif is_buy_time:
        current_price = binance_client.get_price(client,asset)
        order = binance_client.test_buy_asset(client,asset,buy_amount,current_price)

    return order


def look_to_sell(client,asset,current_price,asset_amount,for_real=True):
    time_to_sell = logic.is_sell_time(current_price, asset_amount, buy_amount)
    order = None

    if time_to_sell and for_real:
        order = binance_client.sell_asset(client,asset,asset_amount)
        logic.send_email_update("I sold some "+asset+ " for you!")
    elif time_to_sell:
        order = binance_client.test_sell_asset(client,asset,asset_amount)
    
    return order

    

def main(client):
    for asset in assets_to_check:
        asset_amount = binance_client.get_asset_amount(client, asset)
        current_price = binance_client.get_price(client,asset)
        order = None
        
        if (asset_amount * current_price) > 20:
            print("Already have "+asset+", looking to sell")
            order = look_to_sell(client,asset,current_price,asset_amount)
        else:
            print("Don't have "+asset+", looking to buy")
            order = look_to_buy(client,asset,current_price)

        if order is not None:
            print(order)



if __name__ == '__main__':
    client = binance_client.get_client()
    try:
        while True:
            main(client)
            time.sleep(30)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        logic.send_email_update("I crashed :(")