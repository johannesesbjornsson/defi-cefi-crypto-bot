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


def look_to_sell(asset_object,sell_amount):

    time_to_sell = logic.is_sell_time(asset_object.price, asset_object.asset_holdings, sell_amount)
    order = None
    time_to_sell = True
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
        #else:
        #    gbp_available = binance_client.get_asset_amount(client, "GBP")
        #    if gbp_available > asset_settings["gbp_amount"]:
        #        print("Don't have "+asset+", looking to buy")
        #        order = look_to_buy(client,asset,current_price,asset_settings)
        #    else:
        #        print("Only have "+str(gbp_available)+"to play with, cannot buy "+asset)
        #if order is not None:
        #    print(order)



if __name__ == '__main__':
    client = binance_client.get_client()
    main(client)
    #try:
    #    while True:
    #        main(client)
    #        time.sleep(30)
    #except Exception as e:
    #    tb = traceback.format_exc()
    #    print(tb)
    #    logic.send_email_update("I crashed :(")