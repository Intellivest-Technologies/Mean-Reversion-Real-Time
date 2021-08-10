from tda import auth, client
from tda.orders.equities import equity_buy_market, equity_sell_market
from tda.orders.common import Duration, Session
from webdriver_manager.chrome import ChromeDriverManager
import yfinance as yf
import datetime as dt
from datetime import datetime
import pandas as pd
import numpy as np
from statistics import mean
from statistics import stdev
import json
import schedule
import time
from auth_params import ACCT_NUMBER, API_KEY

#GLOBAL VARIABLES
STOCK = 'VOO'
TIME_PERIOD = 20
portfolio = {}

def auth_func():

    token_path = 'token.pickle'
    api_key = 'UJG9KA2FY4IP0UNROGEBMIMC45HIA7FJ@AMER.OAUTHAP'
    redirect_uri = 'http://localhost'
    try:
        c = auth.client_from_token_file(token_path, API_KEY)
    except FileNotFoundError:
        from selenium import webdriver
        with webdriver.Chrome(ChromeDriverManager().install()) as driver:
            c = auth.client_from_login_flow(
                driver, API_KEY, redirect_uri, token_path)

    return c

def get_MovingAverage(prices, time_period):

    prices = prices[0:time_period]
    ma = mean(prices)
    return ma
    
def get_BBands(prices, time_period):

    prices = prices[0:time_period]
    print(prices)
    ma = get_MovingAverage(prices, time_period)
    std = stdev(prices)
    bup = ma + 2*std
    bdown = ma - 2*std
    return bup, bdown

def get_prices(c, end):

    r = c.get_price_history(STOCK,
        period_type=client.Client.PriceHistory.PeriodType.DAY,
        period=client.Client.PriceHistory.Period.THREE_DAYS,
        frequency_type=client.Client.PriceHistory.FrequencyType.MINUTE,
        frequency=client.Client.PriceHistory.Frequency.EVERY_THIRTY_MINUTES,
        end_datetime= end,
        need_extended_hours_data = False
        )

    assert r.status_code == 200, r.raise_for_status()

    y = r.json()
    y = y["candles"]
    y = json.dumps(y)
    df = pd.read_json(y)

    return df

def get_cur_price(c):

    r = c.get_quote(STOCK)
    assert r.status_code == 200, r.raise_for_status()

    y = r.json()
    price = y[STOCK]["lastPrice"]

    return price

def get_balance(c):

    r = c.get_account(ACCT_NUMBER)
    assert r.status_code == 200, r.raise_for_status()

    y = r.json()

    balance = y['securitiesAccount']['currentBalances']['cashAvailableForTrading']
    roundtrips = y['securitiesAccount']['roundTrips']
    
    return balance, roundtrips

def place_order(c, order_type, shares):

    if order_type == 'buy':
        order_spec = equity_buy_market(STOCK, shares).set_session(Session.NORMAL).set_duration(Duration.DAY).build()
        r = c.place_order(ACCT_NUMBER, order_spec)
        assert r.status_code == 200, r.raise_for_status()

    if order_type == 'sell':
        order_spec = equity_sell_market(STOCK, shares).set_session(Session.NORMAL).set_duration(Duration.DAY).build()
        r = c.place_order(ACCT_NUMBER, order_spec)
        assert r.status_code == 200, r.raise_for_status()

def get_action():

    c = auth_func()
    now = datetime.now()
    print(now)

    df = get_prices(c, now)
    bup, bdown = get_BBands(df.close, TIME_PERIOD)

    #get current price
    price = get_cur_price(c)

    #get account balance
    balance, roundtrips = get_balance(c)

    print("Current balance " + str(balance))
    print("Current price " + str(price))
    print("High Band " + str(bup))
    print("Low Band " + str(bdown))

    #check if roundtrips is less than 2
    if roundtrips < 2:

        if price < bdown:
            if portfolio[STOCK] == 0:
                portfolio[STOCK] = 1
                place_order(c, 'buy', 1)
                print("Bought")

        if price > bup:
            if portfolio[STOCK] == 1:
                portfolio[STOCK] = 0
                place_order(c, 'sell', 1)
                print("Sold")

def main():

    #local
    schedule.every().day.at("07:00").do(get_action)
    schedule.every().day.at("07:30").do(get_action)
    schedule.every().day.at("08:00").do(get_action)
    schedule.every().day.at("08:30").do(get_action)
    schedule.every().day.at("09:00").do(get_action)
    schedule.every().day.at("09:30").do(get_action)
    schedule.every().day.at("10:00").do(get_action)
    schedule.every().day.at("10:30").do(get_action)
    schedule.every().day.at("11:00").do(get_action)
    schedule.every().day.at("11:30").do(get_action)
    schedule.every().day.at("12:00").do(get_action)
    schedule.every().day.at("12:30").do(get_action)
    schedule.every().day.at("13:00").do(get_action)

    #real
    '''
    schedule.every().day.at("14:00").do(get_action)
    schedule.every().day.at("14:30").do(get_action)
    schedule.every().day.at("15:00").do(get_action)
    schedule.every().day.at("15:30").do(get_action)
    schedule.every().day.at("16:00").do(get_action)
    schedule.every().day.at("16:30").do(get_action)
    schedule.every().day.at("17:00").do(get_action)
    schedule.every().day.at("17:30").do(get_action)
    schedule.every().day.at("18:00").do(get_action)
    schedule.every().day.at("18:30").do(get_action)
    schedule.every().day.at("19:00").do(get_action)
    schedule.every().day.at("19:30").do(get_action)
    schedule.every().day.at("20:00").do(get_action)
    '''

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()


