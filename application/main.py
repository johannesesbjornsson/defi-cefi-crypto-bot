import logic
import binance_client
import logging
import time
import traceback

assets_to_check = {
    "BTC": {
        "precision" : 6,
        "gbp_amount" : 50
    },
    "ETH": {
        "precision" : 4,
        "gbp_amount" : 50
    },
    "XRP": {
        "precision" : 1,
        "gbp_amount" : 50
    }
}


def look_to_buy(asset_object,gbp_amount):
    is_buy_time = False
    order = None


    # Move this logic into asset object
    last_hours_data = asset_object.get_last_hours_of_data()
    last_weeks_data = asset_object.get_last_weeks_of_data()

    market_good, average_price_last_period = logic.get_maket_status(last_hours_data,last_weeks_data)
    
    if market_good:
        asset_object.update_price()
        is_buy_time = logic.is_buy_time(average_price_last_period, asset_object.price)
    
    if is_buy_time and asset_object.avaiable_cash > gbp_amount: 
        order = asset_object.test_buy_asset(gbp_amount)
        logic.send_email_update("I bought some "+asset+" for you!")

    return order


def look_to_sell(asset_object,sell_amount):

    # TODO move is_sell_time into asset object
    asset_object.update_price()
    time_to_sell = logic.is_sell_time(asset_object.price, asset_object.asset_holdings, sell_amount)
    order = None
    
    if time_to_sell:
        order = asset_object.test_sell_asset()
    
    return order

    

def main(client):
    for asset in assets_to_check:
        asset_settings = assets_to_check[asset]
        gbp_amount = asset_settings["gbp_amount"]

        asset_object = binance_client.Asset(client,asset,asset_settings["precision"])

        if asset_object.has_active_orders():
            print("Order of "+asset+", in progress")
            continue
        
        if (asset_object.asset_holdings * asset_object.price) > 20:
            print("Already have "+asset+", looking to sell")
            order = look_to_sell(asset_object,gbp_amount)
        else:
            print("Don't have "+asset+", looking to buy")
            order = look_to_buy(asset_object,gbp_amount)

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