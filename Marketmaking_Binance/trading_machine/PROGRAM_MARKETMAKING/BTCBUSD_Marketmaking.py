# -*- coding: utf-8 -*-
import sys, os, certifi
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))))
os.environ['SSL_CERT_FILE'] = certifi.where()
from Spot_trading.spot import Spot as Client
from Spot_trading.websocket.spot.websocket_client import SpotWebsocketClient
from Spot_trading.websocket.binance_socket_manager import BinanceSocketManager
import numpy as np
import time
import logging
from Spot_trading.lib.utils import config_logging
import pandas as pd
import datetime
import time

os.environ['SSL_CERT_FILE'] = certifi.where()


asset_info = {
    "BTCBUSD": {'minQty':0.00001,"minQtydigits": 5,"maxQty": 9000 ,'minPrice':2},
    "ETHBUSD": {'minQty':0.0001,"minQtydigits": 4,"maxQty":9000 ,'minPrice':2},
    "BNBBUSD": {'minQty':0.001,"minQtydigits": 3,"maxQty":900000 ,'minPrice':1},
    "XRPBUSD": {'minQty':1,"minQtydigits": 0,"maxQty":90000,'minPrice':4},
    "ADABUSD": {'minQty':0.1,"minQtydigits": 1,"maxQty":900000 ,'minPrice':4},
    "DOGEBUSD": {'minQty':1,"minQtydigits": 0,"maxQty":9000000 ,'minPrice':5},
    "MATICBUSD": {'minQty':0.1,"minQtydigits": 1,"maxQty":9000000 ,'minPrice':4},
    "DOTBUSD": {'minQty':0.01,"minQtydigits": 2,"maxQty":90000 ,'minPrice':2},
    "TRXBUSD": {'minQty':0.1,"minQtydigits": 1,"maxQty":9000000 ,'minPrice':5},
    "LTCBUSD": {'minQty':0.001,"minQtydigits": 3,"maxQty":90000 ,'minPrice':2},
    "SOLBUSD": {'minQty':0.01,"minQtydigits": 2,"maxQty":90000 ,'minPrice':2},
    "AVAXBUSD": {'minQty':0.01,"minQtydigits": 2,"maxQty":90000 ,'minPrice':2},
    "OPBUSD": {'minQty': 0.01, "minQtydigits": 2, "maxQty": 90000, 'minPrice': 3},

}



class MarketMaker():
    def __init__(self, symbol, api_key, api_secret, n_rate, order_rate, passage_rate, num_orders, MM_ratio):
        self.min_order = 0
        self.max_order = 0
        self.max_request = 0
        self.symbol = symbol
        self.client = Client(api_key, api_secret)  # , base_url="https://testnet.binance.vision") #mainnet
        try:
            self.client.cancel_open_orders(symbol=self.symbol)
            self.max_request += 1
        except:
            pass

        config_logging(logging, logging.DEBUG)
        self.stream = self.ws_client()
        self.bm = BinanceSocketManager(self.client)
        self.balance_array = {self.symbol: {'free': 0, 'locked': 0}, "BUSD": {'free': 0, 'locked': 0}}
        self.asset_balance()
        self.max_request += 10
        self.n_rate = n_rate
        self.order_rate = order_rate
        self.passage_rate = passage_rate
        self.num_orders = num_orders
        self.MM_ratio = MM_ratio
        self.Flag = False
        self.last_buy_filled = 0
        self.last_sell_filled = 0
        self.buy_amt = 0
        self.sell_amt = 0
        order_book = self.client.depth(symbol=self.symbol)
        self.max_request += 1
        self.standard_price = None
        self.balance = 0
        self.order_tracker = 0
        self.left_orders = []
        self.cumulative_sell_amount = 0
        self.cumulative_buy_amount = 0

        while self.standard_price == None:
            self.standard_price = round((float(order_book['bids'][0][0]) + float(order_book['asks'][0][0])) / 2,
                                        asset_info[self.symbol]['minPrice'])
            order_book = self.client.depth(symbol=self.symbol)
            self.max_request += 1


        orderrange = []
        calculation_orderrange = []
        nn_rate = self.n_rate / (num_orders)
        gijunprice = self.standard_price
        for i in range(-num_orders, num_orders + 1):
            orderrange.append(str(round(-i * nn_rate * 100, 4)) + "%")
            calculation_orderrange.append(round(-i * nn_rate, 6))
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        gijun_df = pd.DataFrame(
            columns=['orderrange', 'order_price', 'balance_quantity', 'balance_amount', 'order_quantity',
                     'passage_rate', 'passage_price', 'passage_quantity', 'passage_amount'])
        gijun_df["orderrange"] = orderrange
        gijun_df.loc[num_orders / 2, "order_price"] = self.standard_price
        k = 0
        for i in calculation_orderrange:
            gijun_df.iloc[k, 1] = round(gijunprice * np.exp(i), asset_info[self.symbol]['minPrice'])
            k += 1
        gijunbalance_amount = (float(self.balance_array[self.symbol]['free']) + float(
            self.balance_array[self.symbol]['locked'])) * gijunprice * self.MM_ratio
        # gijunbalance_amount = 96000
        gijun_df["balance_amount"] = gijunbalance_amount
        gijun_df['balance_quantity'] = gijun_df['balance_amount'] / gijun_df['order_price']
        k = 0
        for i in calculation_orderrange:
            gijun_df.iloc[k, 6] = round(gijun_df.iloc[k, 1] * np.exp(self.passage_rate),
                                        asset_info[self.symbol]['minPrice'])
            k += 1
        for i in range(len(gijun_df)):
            index = gijun_df.index[i]
            gijun_df.loc[index, 'balance_quantity'] = round(gijun_df.loc[index, 'balance_quantity'],
                                                            asset_info[self.symbol]['minQtydigits'])
        for i in range(len(gijun_df) - 1):
            index = gijun_df.index[i]
            index_a = gijun_df.index[i + 1]
            gijun_df.loc[index, 'order_quantity'] = gijun_df.loc[index_a, 'balance_quantity'] - gijun_df.loc[
                index, 'balance_quantity']
        # gijun_df.loc["0.0%", order_quantity]
        gijun_df['passage_rate'] = str(round(self.passage_rate * 100, 4)) + "%"
        gijun_df['passage_quantity'] = gijun_df['order_quantity']
        gijun_df.iloc[num_orders + 1:, 4] = gijun_df.iloc[num_orders:-1, 4]
        gijun_df.iloc[num_orders, 4] = 0
        gijun_df.iloc[num_orders, 5] = 0
        gijun_df.iloc[num_orders, 6] = 0
        gijun_df.iloc[num_orders + 1:, 7] = gijun_df.iloc[num_orders:-1, 7]
        gijun_df.iloc[num_orders, 7] = 0
        gijun_df['passage_amount'] = (gijun_df['passage_quantity'] * gijun_df['passage_price'])

        for i in range(len(gijun_df)):
            index = gijun_df.index[i]
            gijun_df.loc[index, 'passage_amount'] = round(gijun_df.loc[index, 'passage_amount'], 2)

        gijun_df['side'] = None
        gijun_df.iloc[0:num_orders, 9] = 'SELL'
        gijun_df.iloc[num_orders + 1:num_orders * 2 + 1, 9] = 'BUY'

        gijun_df['balance_amount'] = gijun_df['order_price'] * gijun_df['balance_quantity']
        print(gijun_df)
        logging.info(f"BINANCE {self.symbol} PROGRAM STARTED")
        logging.info("================SETTINGS================")
        logging.info(f"n_rate                : {self.n_rate}")
        logging.info(f"order_rate            : {self.order_rate}")
        logging.info(f"passage_rate          : {self.passage_rate}")
        logging.info(f"num_orders            : {self.num_orders}")
        logging.info(f"MM ratio              : {self.MM_ratio}")
        logging.info(f"STANDARD PRICE        : {self.standard_price}")
        logging.info(f"NUMBER OF Total Orders      : {self.num_orders * 2}")
        logging.info("========================================")

        self.clock_reset()
        self.mminor_clock_reset()
        self.minor_clock_reset()
        self.major_clock_reset()

        self.df = gijun_df.copy()

        for i in range(len(gijun_df)):
            index = gijun_df.index[i]
            try:
                if gijun_df.loc[index, 'order_price'] < self.standard_price and gijun_df.loc[index, 'side'] == 'BUY':
                    self.client.new_order(symbol=self.symbol, side='buy', type='limit',
                                          quantity=round(gijun_df.loc[index, 'order_quantity'],
                                                         asset_info[self.symbol]['minQtydigits']),
                                          price=round(gijun_df.loc[index, 'order_price'],
                                                      asset_info[self.symbol]['minPrice']))
                    self.max_request += 1
                    self.min_order += 1
                    self.max_order += 1



            except:
                pass
            try:
                if gijun_df.loc[index, 'order_price'] > self.standard_price and gijun_df.loc[index, 'side'] == 'SELL':
                    self.client.new_order(symbol=self.symbol, side='sell', type='limit',
                                          quantity=round(gijun_df.loc[index, 'order_quantity'],
                                                         asset_info[self.symbol]['minQtydigits']),
                                          price=round(gijun_df.loc[index, 'order_price'],
                                                      asset_info[self.symbol]['minPrice']))
                    self.max_request += 1
                    self.min_order += 1
                    self.max_order += 1


            except:
                pass
        logging.info(f"{num_orders * 2} ORDERS SUBMITTED")
        logging.info("WEBSOCKER STARTING")
        logging.info("MARKETMAKING STARTING")

        while True:
            if self.stream.connectionStatus == True:
                if datetime.datetime.now() > stop3:
                    self.mminor_clock_reset()
                if datetime.datetime.now() > stop2:
                    self.minor_clock_reset()
                if datetime.datetime.now() > stop1:
                    self.major_clock_reset()
                if datetime.datetime.now() > stop:
                    self.bm.stop_socket(self.stream)
                    self.bm.close()
                    self.stream.close()
                    self.clock_reset()

                if datetime.datetime.now().minute%15 == 0 and datetime.datetime.now().second == 0:
                    if self.Flag == False:
                        self.Flag = True
                        #renew listenkey
                        self.client.renew_listen_key(self.response["listenKey"])
                if datetime.datetime.now().minute%14 == 0 and datetime.datetime.now().second == 0:
                    if self.Flag == True:
                        self.Flag = False
            elif self.stream.connectionStatus == False:
                self.bm.stop_socket(self.stream)
                self.bm.close()
                self.stream.close()
                self.stream = self.ws_client()
                self.rebalancing()


            if self.min_order < 50 - len(self.left_orders):
                if len(self.left_orders) > 0:
                    count = len(self.left_orders)
                    for i in range(count):
                        self.message_handler(self.left_orders[0])
                        del self.left_orders[0]

    def message_handler(self,mes):
        print(mes)
        print("The cumulative number of orders : ", self.order_tracker)

        if self.min_order < 50 or self.max_order < 160000 or self.max_request < 1200:
            try:
                    if mes['e'] == 'executionReport':
                        if mes['s'] == self.symbol:
                            #Order executed partially or fully filled
                            if mes['x'] == "TRADE":
                                if mes['S'] == "BUY":
                                    self.cumulative_buy_amount += float(mes['l'])
                                    if round(float(mes['p']),asset_info[self.symbol]['minPrice']) == self.df.iloc[num_orders*2, 1]:
                                        self.last_buy_filled += float(mes['l'])
                                    if round(float(mes['p']), asset_info[self.symbol]['minPrice']) == self.df.iloc[num_orders * 2 -1, 1] and self.last_buy_filled > 0:
                                        self.last_buy_filled -= float(mes['l'])

                                    if round(self.last_buy_filled,asset_info[self.symbol]['minQtydigits']) == round(self.df.iloc[num_orders*2, 4],asset_info[self.symbol]['minQtydigits']) :
                                        self.standard_price = self.df.iloc[num_orders*2, 1]
                                        self.balance = self.df.iloc[num_orders * 2, 2]
                                        self.last_buy_filled = 0
                                        self.rebalancing()

                                    else:
                                        try:
                                            order_quantity = round(float(mes['l']) + self.sell_amt,asset_info[self.symbol]['minQtydigits'])
                                            order_price = round(float(mes['p']) * np.exp(passage_rate),asset_info[self.symbol]['minPrice'])
                                            self.client.new_order(symbol=self.symbol, type='limit',side='sell', quantity=order_quantity, price=order_price)
                                            self.sell_amt = 0
                                            self.min_order += 1
                                            self.max_order += 1
                                            self.max_request += 1
                                            self.order_tracker += 1
                                        except:
                                            self.sell_amt += float(mes['l'])
                                if mes['S'] == "SELL":
                                    self.cumulative_sell_amount += float(mes['l'])
                                    if round(float(mes['p']),asset_info[self.symbol]['minPrice']) == self.df.iloc[0,1]:
                                        self.last_sell_filled += float(mes['l'])
                                    if round(float(mes['p']), asset_info[self.symbol]['minPrice']) == self.df.iloc[1, 1] and self.last_sell_filled >0:
                                        self.last_sell_filled -= float(mes['l'])

                                    if round(self.last_sell_filled,asset_info[self.symbol]['minQtydigits']) == round(self.df.iloc[0,4],asset_info[self.symbol]['minQtydigits']):
                                        self.standard_price = self.df.iloc[0,1]
                                        self.balance = self.df.iloc[0, 2]
                                        self.last_sell_filled = 0
                                        self.rebalancing()
                                    else:
                                        try:
                                            order_quantity = round(float(mes['l'])+ self.buy_amt,asset_info[self.symbol]['minQtydigits'])
                                            order_price = round(float(mes['p']) * np.exp(-passage_rate), asset_info[self.symbol]['minPrice'])
                                            self.client.new_order(symbol=self.symbol, type='limit',side='buy', quantity=order_quantity, price=order_price)
                                            self.buy_amt = 0
                                            self.min_order += 1
                                            self.max_order += 1
                                            self.max_request += 1
                                            self.order_tracker += 1
                                        except:
                                            self.buy_amt += float(mes['l'])
            except:
                pass
        else:
            self.left_orders.append(mes)


    #major 1 day = 160,000 limit
    def major_clock_reset(self):
        global stop1
        stop1 = (datetime.datetime.now() + datetime.timedelta(hours=24))
        self.max_order = 0
    #minor 10 seconds = 50 limit
    def minor_clock_reset(self):
        global stop2
        stop2 = (datetime.datetime.now() + datetime.timedelta(seconds=10))
        self.min_order = 0
    #1200 requests per min
    def mminor_clock_reset(self):
        global stop3
        stop3 = (datetime.datetime.now() + datetime.timedelta(minutes=1))
        self.max_request = 0
    #websocket reset function
    def clock_reset(self):
        global stop
        stop = (datetime.datetime.now() + datetime.timedelta(hours=6))

    def ws_client(self):
        self.response = self.client.new_listen_key()
        stream = pd.read_csv(os.path.dirname(os.path.abspath(
            os.path.dirname(os.path.abspath(os.path.dirname(__file__))))) + "/config.csv")['websocket'][0]
        logging.info("Receving listen key : {}".format(self.response["listenKey"]))
        ws_client = SpotWebsocketClient(stream_url=stream)
        ws_client.start()
        ws_client.user_data(
            listen_key=self.response["listenKey"],
            id=1,
            callback=self.message_handler,
        )

        return ws_client
    def rebalancing(self):
        try:
            self.client.cancel_open_orders(symbol=self.symbol)
            self.max_request += 1
        except:
            pass

        self.max_request += 10
        self.Flag = False
        orderrange = []
        calculation_orderrange = []
        nn_rate = self.n_rate / (num_orders)
        gijunprice = self.standard_price
        for i in range(-num_orders, num_orders + 1):
            orderrange.append(str(round(-i * nn_rate * 100, 4)) + "%")
            calculation_orderrange.append(round(-i * nn_rate, 6))
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        gijun_df = pd.DataFrame(
            columns=['orderrange', 'order_price', 'balance_quantity', 'balance_amount', 'order_quantity',
                     'passage_rate', 'passage_price', 'passage_quantity', 'passage_amount'])
        gijun_df["orderrange"] = orderrange
        gijun_df.loc[num_orders / 2, "order_price"] = self.standard_price
        k = 0
        for i in calculation_orderrange:
            gijun_df.iloc[k, 1] = round(gijunprice * np.exp(i), asset_info[self.symbol]['minPrice'])
            k += 1
        gijunbalance_amount = (float(self.balance_array[self.symbol]['free']) + float(
            self.balance_array[self.symbol]['locked'])) * gijunprice * self.MM_ratio
        # gijunbalance_amount = 96000
        gijun_df["balance_amount"] = gijunbalance_amount
        gijun_df['balance_quantity'] = gijun_df['balance_amount'] / gijun_df['order_price']
        k = 0
        for i in calculation_orderrange:
            gijun_df.iloc[k, 6] = round(gijun_df.iloc[k, 1] * np.exp(self.passage_rate),
                                        asset_info[self.symbol]['minPrice'])
            k += 1
        for i in range(len(gijun_df)):
            index = gijun_df.index[i]
            gijun_df.loc[index, 'balance_quantity'] = round(gijun_df.loc[index, 'balance_quantity'],
                                                            asset_info[self.symbol]['minQtydigits'])
        for i in range(len(gijun_df) - 1):
            index = gijun_df.index[i]
            index_a = gijun_df.index[i + 1]
            gijun_df.loc[index, 'order_quantity'] = gijun_df.loc[index_a, 'balance_quantity'] - gijun_df.loc[
                index, 'balance_quantity']
        # gijun_df.loc["0.0%", order_quantity]
        gijun_df['passage_rate'] = str(round(self.passage_rate * 100, 4)) + "%"
        gijun_df['passage_quantity'] = gijun_df['order_quantity']
        gijun_df.iloc[num_orders + 1:, 4] = gijun_df.iloc[num_orders:-1, 4]
        gijun_df.iloc[num_orders, 4] = 0
        gijun_df.iloc[num_orders, 5] = 0
        gijun_df.iloc[num_orders, 6] = 0
        gijun_df.iloc[num_orders + 1:, 7] = gijun_df.iloc[num_orders:-1, 7]
        gijun_df.iloc[num_orders, 7] = 0
        gijun_df['passage_amount'] = (gijun_df['passage_quantity'] * gijun_df['passage_price'])

        for i in range(len(gijun_df)):
            index = gijun_df.index[i]
            gijun_df.loc[index, 'passage_amount'] = round(gijun_df.loc[index, 'passage_amount'], 2)

        gijun_df['side'] = None
        gijun_df.iloc[0:num_orders, 9] = 'SELL'
        gijun_df.iloc[num_orders + 1:num_orders * 2 + 1, 9] = 'BUY'

        gijun_df['balance_amount'] = gijun_df['order_price'] * gijun_df['balance_quantity']
        print(gijun_df)
        logging.info(f"BINANCE {self.symbol} PROGRAM STARTED")
        logging.info("================SETTINGS================")
        logging.info(f"n_rate                : {self.n_rate}")
        logging.info(f"order_rate            : {self.order_rate}")
        logging.info(f"passage_rate          : {self.passage_rate}")
        logging.info(f"num_orders            : {self.num_orders}")
        logging.info(f"MM ratio              : {self.MM_ratio}")
        logging.info(f"STANDARD PRICE        : {self.standard_price}")
        logging.info(f"NUMBER OF Total Orders      : {self.num_orders * 2}")
        logging.info("========================================")

        for i in range(len(gijun_df)):
            index = gijun_df.index[i]
            while self.min_order > 10 or self.max_order > 160000 or self.max_request > 1200:
                pass
            try:
                if gijun_df.loc[index, 'order_price'] < self.standard_price and gijun_df.loc[index, 'side'] == 'BUY':
                    self.client.new_order(symbol=self.symbol, side='buy', type='limit',
                                          quantity=round(gijun_df.loc[index, 'order_quantity'],
                                                         asset_info[self.symbol]['minQtydigits']),
                                          price=round(gijun_df.loc[index, 'order_price'],
                                                      asset_info[self.symbol]['minPrice']))
                    self.max_request += 1
                    self.min_order += 1
                    self.max_order += 1

            except:
                pass
            try:
                if gijun_df.loc[index, 'order_price'] > self.standard_price and gijun_df.loc[index, 'side'] == 'SELL':
                    self.client.new_order(symbol=self.symbol, side='sell', type='limit',
                                          quantity=round(gijun_df.loc[index, 'order_quantity'],
                                                         asset_info[self.symbol]['minQtydigits']),
                                          price=round(gijun_df.loc[index, 'order_price'],
                                                      asset_info[self.symbol]['minPrice']))
                    self.max_request += 1
                    self.min_order += 1
                    self.max_order += 1

            except:
                pass
        logging.info(f"{num_orders * 2} ORDERS SUBMITTED")
        logging.info("WEBSOCKER STARTING")
        logging.info("MARKETMAKING STARTING")

        self.df = gijun_df.copy()

    def asset_balance(self):
        '''
        Return cryptocurrency balances
        '''
        Balances = self.client.account()['balances']
        for i in Balances:
            try:
                if i['asset'] == self.symbol[:-4]:
                    self.balance_array[self.symbol]['locked'] = (float(i['locked']))
                    self.balance_array[self.symbol]['free'] = (float(i['free']))
            except:
                pass
            try:
                if i['asset'] == 'BUSD':
                    self.balance_array["BUSD"]['locked'] = (float(i['locked']))
                    self.balance_array["BUSD"]['free'] = (float(i['free']))
            except:
                pass






if __name__ == "__main__":
    symbol = "BTCBUSD"
    api_key = pd.read_csv(os.path.dirname(os.path.abspath(
        os.path.dirname(os.path.abspath(os.path.dirname(__file__))))) + "/config.csv")['api'][0]
    api_secret = pd.read_csv(os.path.dirname(os.path.abspath(
        os.path.dirname(os.path.abspath(os.path.dirname(__file__))))) + "/config.csv")['secret'][0]
    n_rate = 0.002
    order_rate = 0.0002
    passage_rate = 0.0002
    num_orders = 10
    MM_ratio = 1
    MarketMaker(symbol = symbol, api_key =api_key, api_secret= api_secret,n_rate = n_rate, order_rate=order_rate, passage_rate=passage_rate, num_orders=num_orders,MM_ratio=MM_ratio)
