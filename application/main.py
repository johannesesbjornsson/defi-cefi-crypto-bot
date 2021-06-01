import logic
import binance_client
import logging
import time
import traceback

assets_to_check = {
    #"BTC": {
    #    "precision" : 6,
    #    "gbp_amount" : 50
    #},
    "ETH": {
        "precision" : 5,
        "gbp_amount" : 50
    },
    "XRP": {
        "precision" : 5,
        "gbp_amount" : 50
    }
}


def look_to_buy(client,asset,current_price,asset_settings):
    buy_amount = asset_settings["gbp_amount"]
    precision = asset_settings["precision"]
    is_buy_time = False
    order = None

    last_hours_data = binance_client.get_last_hours_of_data(client,asset)
    last_weeks_data = binance_client.get_last_weeks_of_data(client,asset)

    market_good, average_price_last_period = logic.get_maket_status(last_hours_data,last_weeks_data)

    if market_good:
        is_buy_time = logic.is_buy_time(average_price_last_period,current_price)
    
    if is_buy_time:
        current_price = binance_client.get_price(client,asset)
        order = binance_client.buy_asset(client,asset,buy_amount,current_price,precision)
        logic.send_email_update("I bought some "+asset+" for you!")

    return order


def look_to_sell(client,asset,current_price,asset_amount,asset_settings):
    sell_amount = asset_settings["gbp_amount"]
    precision = asset_settings["precision"]

    time_to_sell = logic.is_sell_time(current_price, asset_amount, sell_amount)
    order = None

    if time_to_sell:
        order = binance_client.sell_asset(client,asset,asset_amount,current_price,precision)
        logic.send_email_update("I sold some "+asset+ " for you!")
    
    return order

    

def main(client):
    for asset in assets_to_check:
        asset_settings = assets_to_check[asset]

        orders = binance_client.get_orders(client, asset)
        active_order = logic.get_active_orders(orders)

        if active_order:
            print("Order of "+asset+", in progress")
            continue

        asset_amount = binance_client.get_asset_amount(client, asset)
        
        current_price = binance_client.get_price(client,asset)
        order = None
        
        if (asset_amount * current_price) > 20:
            print("Already have "+asset+", looking to sell")
            order = look_to_sell(client,asset,current_price,asset_amount,asset_settings)
        else:
            gbp_available = binance_client.get_asset_amount(client, "GBP")
            if gbp_available > asset_settings["gbp_amount"]:
                print("Don't have "+asset+", looking to buy")
                order = look_to_buy(client,asset,current_price,asset_settings)
            else:
                print("Only have "+str(gbp_available)+"to play with, cannot buy "+asset)


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