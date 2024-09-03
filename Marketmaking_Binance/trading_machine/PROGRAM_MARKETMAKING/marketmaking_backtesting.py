#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import json
import time
import hashlib, hmac, base64
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import pandas_ta as ta
import re
import math
import matplotlib.pyplot as plt

# In[2]:


start = '2022-11-27'
end = '2022-11-28'
limit = 499


# In[3]:


def time_to_timestamp(s):
    return round(datetime.strptime(s + ' 00:00:00', '%Y-%m-%d %H:%M:%S').timestamp() * 1000)


def interval_to_milliseconds(interval):
    if interval == '1m':
        return 1 * 60 * 1000
    elif interval == '3m':
        return 3 * 60 * 1000
    elif interval == '5m':
        return 5 * 60 * 1000
    elif interval == '15m':
        return 15 * 60 * 1000
    elif interval == '30m':
        return 30 * 60 * 1000
    elif interval == '1h':
        return 60 * 60 * 1000
    elif interval == '2h':
        return 2 * 60 * 60 * 1000
    elif interval == '4h':
        return 4 * 60 * 60 * 1000
    elif interval == '6h':
        return 6 * 60 * 60 * 1000
    elif interval == '8h':
        return 8 * 60 * 60 * 1000
    elif interval == '12h':
        return 12 * 60 * 60 * 1000
    elif interval == '1d':
        return 24 * 60 * 60 * 1000
    elif interval == '3d':
        return 3 * 24 * 60 * 60 * 1000
    elif interval == '1w':
        return 7 * 24 * 60 * 60 * 1000


# In[4]:

def testing(ticker):
    # Get 1m ohlcv from binance
    interval = '1m'
    interval_in_milliseconds = interval_to_milliseconds(interval)
    start_time = time_to_timestamp(start) - interval_to_milliseconds('5m') * 200
    end_time = 0

    data1 = pd.DataFrame(columns=["Time", "Open", "High", "Low", "Close", "Volume"])

    while end_time < time_to_timestamp(end):
        end_time = min(start_time + interval_in_milliseconds * limit, time_to_timestamp(end))

        r = requests.get('https://api.binance.com/api/v3/klines?symbol=' + ticker + '&interval='
                         + interval + '&startTime=' + str(start_time) + '&endTime=' + str(end_time))
        json_data = r.json()
        array_data = np.array(json_data)
        data1 = pd.concat(
            [data1, pd.DataFrame(array_data[:, :6], columns=["Time", "Open", "High", "Low", "Close", "Volume"])])
        start_time = end_time + interval_in_milliseconds

    # convert unix time back into readable time
    data1['Time'] = pd.to_datetime(data1['Time'], unit='ms')
    data1 = data1.set_index('Time')

    data1['Open'] = data1['Open'].astype(float)
    data1['High'] = data1['High'].astype(float)
    data1['Low'] = data1['Low'].astype(float)
    data1['Close'] = data1['Close'].astype(float)
    data1['Volume'] = data1['Volume'].astype(float)

    ohlc = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
    data1 = data1.loc[start:]

    print(data1)

# In[5]:


#####################settings

    initial_value = 10000
    orders_num = 50
    order_rate = 0.001
    passage_rate = 0.001
    mm_rate = 1

    b_price = []
    b_amount = []
    a_price = []
    a_amount = []

    for j in range(orders_num + 1, 0, -1):
        if j == orders_num + 1:
            b_price.append(math.exp(-j * order_rate))
            b_amount.append(0)
        else:
            b_price.append(math.exp(-j * order_rate))
            b_amount.append(math.exp(j * order_rate))

    for i in range(1, orders_num + 2):
        if i == orders_num + 1:
            a_price.append(math.exp(i * order_rate))
            a_amount.append(0)
        else:
            a_price.append(math.exp(i * order_rate))
            a_amount.append(math.exp(-i * order_rate))

        # In[6]:

    portfolio = pd.DataFrame(columns=[ticker, "BUSD", "Total_value_in_BUSD"], index=data1.index)

    for i in range(0, len(data1.index)):
        index = data1.index[i]
        index_b = data1.index[i - 1]
        one_day_time = index - timedelta(hours=index.hour) - timedelta(minutes=index.minute)

        if one_day_time == index:
            # print(one_day_time)
            if i == 0:
                base_price = data1.loc[index, 'Open']
                base_amount = initial_value / base_price / 2
                portfolio[ticker][index] = base_amount
                portfolio['BUSD'][index] = initial_value / 2
            else:
                base_price = data1.loc[index, 'Open']
                base_amount = portfolio.loc[index_b, 'Total_value_in_BUSD'] / base_price / 2
                portfolio[ticker][index] = portfolio[ticker][index_b]
                portfolio['BUSD'][index] = portfolio['BUSD'][index_b]
            making_buy_orders = pd.DataFrame(
                {"prices": b_price + [1] + a_price, "amount": b_amount + [0] * (orders_num + 2),
                 "exit_prices": [0] * (orders_num * 2 + 3)})
            making_buy_orders['prices'] = making_buy_orders['prices'] * base_price
            making_buy_orders['amount'] = making_buy_orders['amount'] * base_amount
            making_buy_orders['amount'] = making_buy_orders['amount'] - making_buy_orders.shift(-1)['amount']
            making_buy_orders.loc[0, 'amount'] = 0
            making_buy_orders.loc[orders_num, 'amount'] = base_amount * math.exp(order_rate) - base_amount
            making_buy_orders.loc[orders_num * 2 + 2, 'amount'] = 0
            # print(sum(making_buy_orders['prices']*making_buy_orders['amount']))
            # print(portfolio['BUSD'][index])
            if portfolio['BUSD'][index] < sum(making_buy_orders['prices'] * making_buy_orders['amount']):
                making_buy_orders['amount'] = 0
                print(making_buy_orders)
            making_buy_orders['exit_prices'] = making_buy_orders['prices'] * math.exp(passage_rate)

            making_sell_orders = pd.DataFrame(
                {"prices": b_price + [1] + a_price, "amount": [0] * (orders_num + 2) + a_amount,
                 "exit_prices": [0] * (orders_num * 2 + 3)})
            making_sell_orders['prices'] = making_sell_orders['prices'] * base_price
            if portfolio[ticker][index] > (a_amount[0] - a_amount[-2]) * base_amount:
                making_sell_orders['amount'] = making_sell_orders['amount'] * base_amount
                making_sell_orders['amount'] = making_sell_orders.shift(1)['amount'] - making_sell_orders['amount']
                making_sell_orders.loc[0, 'amount'] = 0
                making_sell_orders.loc[orders_num + 2, 'amount'] = base_amount - base_amount * math.exp(-order_rate)
                making_sell_orders.loc[orders_num * 2 + 2, 'amount'] = 0
            else:
                making_sell_orders['amount'] = 0
            making_sell_orders['exit_prices'] = making_sell_orders['prices'] / math.exp(passage_rate)
            print(making_buy_orders)
            print(making_sell_orders)
        else:
            portfolio[ticker][index] = portfolio[ticker][index_b]
            portfolio['BUSD'][index] = portfolio['BUSD'][index_b]

        new_sell_orders = pd.DataFrame(columns=["prices", "amount", "index_num"])
        new_buy_orders = pd.DataFrame(columns=["prices", "amount", "index_num"])
        for j in making_buy_orders.index:
            if j == len(making_buy_orders.index) - 1:
                pass
            elif (data1['Low'][index] < making_buy_orders.loc[j, 'prices']):
                if (making_buy_orders.loc[j, 'amount'] != 0):
                    portfolio[ticker][index] = portfolio[ticker][index] + making_buy_orders.loc[j, 'amount']
                    portfolio['BUSD'][index] = portfolio['BUSD'][index] - making_buy_orders.loc[j, 'amount'] * \
                                               making_buy_orders.loc[j, 'prices']
                    # new_sell_orders.loc[len(new_sell_orders)] = [making_buy_orders.loc[j, 'exit_prices'], making_buy_orders.loc[j, 'amount'], j+1]
                    new_sell_orders = pd.concat([new_sell_orders,
                                                 pd.DataFrame([[making_buy_orders.loc[j, 'exit_prices'],
                                                                making_buy_orders.loc[j, 'amount'], j + 1]],
                                                              columns=new_sell_orders.columns)], ignore_index=True)
                    making_buy_orders.loc[j, 'amount'] = 0
        for j in making_sell_orders.index:
            if j == 0:
                pass
            elif data1['High'][index] > making_sell_orders.loc[j, 'prices']:
                if (making_sell_orders.loc[j, 'amount'] != 0):
                    portfolio[ticker][index] = portfolio[ticker][index] - making_sell_orders.loc[j, 'amount']
                    portfolio['BUSD'][index] = portfolio['BUSD'][index] + making_sell_orders.loc[j, 'amount'] * \
                                               making_sell_orders.loc[j, 'prices']
                    new_buy_orders.loc[len(new_buy_orders)] = [making_sell_orders.loc[j, 'exit_prices'],
                                                               making_sell_orders.loc[j, 'amount'], j - 1]
                    making_sell_orders.loc[j, 'amount'] = 0

        for k in new_buy_orders.index:
            making_buy_orders.loc[new_buy_orders['index_num'][k], 'amount'] += new_buy_orders.loc[k, 'amount']

        for k in new_sell_orders.index:
            making_sell_orders.loc[new_sell_orders['index_num'][k], 'amount'] += new_sell_orders.loc[k, 'amount']

        portfolio['Total_value_in_BUSD'][index] = portfolio[ticker][index] * data1['Close'][index] + portfolio['BUSD'][index]

    # In[7]:


    pd.set_option('display.max_row', None)
    pd.set_option('display.max_columns', None)

    # In[8]:


    plt.figure(figsize=(18, 6))
    plt.plot(portfolio.index, portfolio['Total_value_in_BUSD'])
    plt.title("PF Value")
    # plt.xticks(rotation=45)
    plt.show()
    print(portfolio['Total_value_in_BUSD'][-1])
    print(portfolio[ticker][-1])
    print(portfolio['BUSD'][-1])

    # In[9]:


    plt.figure(figsize=(18, 6))
    plt.plot(portfolio.index, portfolio[ticker])
    plt.title("PF Value")
    # plt.xticks(rotation=45)
    plt.show()

    # In[10]:


    plt.figure(figsize=(18, 6))
    plt.plot(portfolio.index, portfolio['BUSD'])
    plt.title("PF Value")
    # plt.xticks(rotation=45)
    plt.show()

# In[11]:


testing("BUSDDAI")
# In[ ]:




