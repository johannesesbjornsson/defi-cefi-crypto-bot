import logic
import binance_client
import binance_market_client
import logging
import time
import traceback
import application_config as cfg

from requests.exceptions import ReadTimeout, ConnectionError


def buy(asset_object):
    #order = asset_object.buy_asset()
    order = asset_object.test_buy_asset()
    if order is not None:
        #logic.send_email_update("I bought some "+asset_object.asset+" for you!",cfg.email_api_key)
        print("I bought some "+asset_object.asset+" for you!")
    return order 

def sell(asset_object):
    #order = asset_object.sell_asset()
    order = asset_object.test_sell_asset()
    if order is not None:
        #logic.send_email_update("I sold "+asset_object.asset+" for you!",cfg.email_api_key)
        print("I sold "+asset_object.asset+" for you!")
    return order
    

def main(client,assets_to_check):
    for asset in assets_to_check:
        print("Looking at "+ asset)
        order = None
        asset_settings = assets_to_check[asset]

        asset_object = binance_client.Asset(client,
            asset=asset_settings["crypto"],
            purchase_amount=20,
            currency=asset_settings["currency"]
            )
        market_object = binance_market_client.Market(asset_object,
            number_of_double_downs=asset_settings["double_downs"],
            short_time_compare_mins=asset_settings["short_period_to_compare"], 
            medium_time_compare_hours=asset_settings["medium_period_to_compare"]
        )
        

        if asset_object.has_active_orders():
            print("Order of "+asset+", in progress")
            continue
        
        time_to_sell = market_object.is_sell_time()

        if time_to_sell:
            asset_object.update_price()
            order = sell(asset_object)
        else:
            market_object.set_market_data()
            time_to_buy = market_object.is_buy_time()
            asset_object.update_price()
            if time_to_buy:
                order = buy(asset_object)

        if order is not None:
            print(order)



if __name__ == '__main__':
    client = binance_client.get_client(cfg.api_key,cfg.api_secret)
    print("Starting application")
    
    while True:
        try:
            main(client,cfg.cryptopairs)
        except ReadTimeout as e:
            print("Got connection timout, conntinuing")
        except ConnectionError as e:
            print("Got connection error, conntinuing")
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            print("Sending email crash update")
            #logic.send_email_update("I crashed :(",cfg.email_api_key)
            break

        time.sleep(20)

# Fix this
#requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='api.binance.com', port=443): Read timed out. (read timeout=10)
#requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))