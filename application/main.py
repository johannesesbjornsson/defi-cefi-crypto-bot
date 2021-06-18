import logic
import binance_client
import logging
import time
import traceback
import application_config as cfg

from requests.exceptions import ReadTimeout, ConnectionError


def buy(asset_object):
    #order = asset_object.buy_asset()
    #order = asset_object.test_buy_asset()
    if order is not None:
        logic.send_email_update("I bought some "+asset_object.asset+" for you!",cfg.email_api_key)
        print("I bought some "+asset_object.asset+" for you!")
    return order 

def sell(asset_object):
    #order = asset_object.sell_asset()
    #order = asset_object.test_sell_asset()
    if order is not None:
        logic.send_email_update("I sold "+asset_object.asset+" for you!",cfg.email_api_key)
        print("I sold "+asset_object.asset+" for you!")
    return order 


#def look_to_buy(asset_object,market_object):
#    print("--- Don't have "+asset_object.asset+", looking to buy ---")
#    is_buy_time = False
#    order = None
#
#    market_object.set_market_data()
#    market_object.asset_object.update_price()
#    is_buy_time = market_object.is_buy_time()
#    
#    if is_buy_time:
#        order = buy(asset_object)
#    
#    return order
#
#
#def look_to_sell(asset_object):
#    print("--- Already have "+asset_object.asset+", looking to sell ---")
#    asset_object.update_price()
#    time_to_sell = asset_object.is_sell_time()
#    order = None
#
#    if time_to_sell:
#        order = sell(asset_object)
#    else:
#        asset_object.update_price()
#        if asset_object.double_down() == True:
#            print("Doubling down on "+asset_object.asset)
#            order = buy(asset_object)
#                
#    
#    return order

    

def main(client,assets_to_check):
    for asset in assets_to_check:
        order = None
        asset_settings = assets_to_check[asset]

        asset_object = binance_client.Asset(client,asset,asset_settings["precision"])
        market_object = binance_client.Market(asset_object)
        print("Looking at "+ asset_object.asset)

        if asset_object.has_active_orders():
            print("Order of "+asset+", in progress")
            continue
        
        time_to_sell = asset_object.is_sell_time()

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
            main(client,cfg.assets_to_check)
        except ReadTimeout as e:
            print("Got connection timout, conntinuing")
        except ConnectionError as e:
            print("Got connection error, conntinuing")
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            print("Sending email crash update")
            logic.send_email_update("I crashed :(",cfg.email_api_key)
            break

        time.sleep(20)

# Fix this
#requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='api.binance.com', port=443): Read timed out. (read timeout=10)
#requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))