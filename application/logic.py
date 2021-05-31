import datetime
import logging

import sendgrid
import os
from sendgrid.helpers.mail import *

def send_email_update(message):
    email_api_key = os.environ.get('email_api_key')
    sg = sendgrid.SendGridAPIClient(api_key=email_api_key)
    from_email = Email("johannes.esbjornsson@gmail.com")
    to_email = To("johannes.esbjornsson@gmail.com")
    subject = "Crypto Update"
    content = Content("text/plain", message)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())      

def get_average_price(data):
    total_price = 0.00 
    for entry in data:
        total_price += float(entry[4])
    #    timestamp = datetime.datetime.fromtimestamp(int(entry[0]/1000)).strftime('%c')
    #    print(timestamp, entry[4])
    #print("---")

    average_price = total_price / len(data)
    return average_price

def get_maket_status(last_hours_data,last_weeks_data):
    average_price_thee_hour = get_average_price(last_hours_data)
    average_price_last_period = get_average_price(last_hours_data[-10:])
    average_price_last_week = get_average_price(last_weeks_data)
    market_good = False
    market_too_tot = True
    high_compared_to_last_week = True

    #print("Last period compared to hours", average_price_last_period/average_price_thee_hour)
    if (average_price_last_period/average_price_thee_hour) < 0.99:
        market_too_tot = False

    #print("Last Week compared to hours", average_price_thee_hour/average_price_last_week)

    if (average_price_thee_hour/average_price_last_week) < 1.06:
        high_compared_to_last_week = False

    if market_too_tot == False and high_compared_to_last_week == False:
        market_good = True

    print("No buy time, market_too_tot, high_compared_to_last_week",market_too_tot,high_compared_to_last_week )

    return market_good, average_price_last_period

def is_buy_time(average_price_last_period,current_price):
    is_buy_time = False
    if current_price/average_price_last_period < 0.995:
        is_buy_time =  True

    return is_buy_time

def is_sell_time(current_price, asset_amount, buy_amount):
    is_sell_time = False

    current_holding_value = current_price * asset_amount

    if (current_holding_value / buy_amount) > 1.02:
        print("Selling asset at ", current_holding_value / buy_amount) 
        is_sell_time = True
    else:
        print("Asset value is currently too low", current_holding_value / buy_amount)  


    return is_sell_time

def get_active_orders(orders):
    active_order_exist = False
    for order in orders:
        if order["status"] == "ACTIVE":
            active_order_exist = True
    return active_order_exist
