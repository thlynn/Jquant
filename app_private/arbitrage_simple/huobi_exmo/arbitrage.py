import time
from decimal import Decimal

from app.arbitrage_simple.huobi_okex.trade import Trade
from config import Keys
import queue
from datetime import datetime
import numpy as np

from api.huobi.HuobiDMService import HuobiDM
import api.okex.futures_api as future


class Arbitrage:

    def __init__(self, side_1, side_2, base_symbol, quote_symbol):
        self.base_symbol = base_symbol
        self.quote_symbol = quote_symbol
        self.side_1 = side_1
        self.side_2 = side_2

    def run_thread(self, cls):
        t = cls(self.base_symbol, self.quote_symbol)
        t.start()
        return t

    def monitor(self):
        t1 = self.run_thread(self.side_1)
        t2 = self.run_thread(self.side_2)
        while True:
            time.sleep(1)
            t1, t2 = self.is_alive(t1, t2)
            if t1.timestamp and t2.timestamp:
                self.__class__.is_available(t1, t2)
                # print(t1.name, t1.timestamp, t1.close)
                # print(t2.name, t2.timestamp, t2.close)
                if abs(t1.close - t2.close) > Decimal('80'):
                    print(abs(t1.close - t2.close))
                    print(t1.name, t1.timestamp, t1.close)
                    print(t2.name, t2.timestamp, t2.close)
                    print('\n')

    @staticmethod
    def is_available(t1, t2):
        now = datetime.now().timestamp()
        if t1.timestamp and now - t1.timestamp > 70:
            print(t1.name, 'Unknown Error')
            t1.timestamp = None
        if t2.timestamp and now - t2.timestamp > 70:
            print(t2.name, 'Unknown Error')
            t2.timestamp = None

    def is_alive(self, t1, t2):
        if not t1.is_alive():
            print(t1.name, 'Restart')
            t1 = self.run_thread(self.side_1)
        if not t2.is_alive():
            print(t2.name, 'Restart')
            t2 = self.run_thread(self.side_2)

        return t1, t2

#
# q = queue.Queue(20)
# pos = {'pos_huobi': 0, 'pos_okex': 0, 'flag_huobi': 1, 'flag_okex': 1}
#
# dm = HuobiDM(Keys.URL, Keys.ACCESS_KEY, Keys.SECRET_KEY)
#
# futureAPI = future.FutureAPI(
#     Keys.api_key, Keys.seceret_key, Keys.passphrase, True)
#
# leverage = 10
# trades = [Trade(pos, q, dm, futureAPI, leverage) for i in range(4)]
# trades[0].init_pos()
# for trade in trades:
#     trade.start()
#
# mean = -3
# ran = 30
# # h - l = ran
# # h + l = 2*mean
# A = np.mat('1,-1; 1,1')
# b = np.mat('{}, {}'.format(ran, 2*mean)).T
# r = np.linalg.solve(A, b)
# high = r[0, 0]
# low = r[1, 0]
# high_cross = [high, high+4, high+8]
# low_cross = [low, low-2, low-4]
#
# while True:
#     traded = 0
#     if thread_okex.timestamp == thread_huobi.timestamp \
#             and thread_huobi.close is not None \
#             and thread_okex.close is not None:
#         spread = thread_huobi.close - thread_okex.close
#         if pos['flag_huobi'] and pos['flag_okex']:
#             dic1 = {high_cross[0]: leverage,
#                     high_cross[1]: 2*leverage,
#                     high_cross[2]: 3*leverage}
#             for key in dic1.keys():
#                 if spread > key and not traded:
#                     if (pos['pos_huobi'] > dic1[key]*(-1)
#                             and pos['pos_huobi'] <= 0):
#                         q.put(('sell', 'huobi', thread_huobi.close, 1))
#                         traded = 1
#                         print(
#                             datetime.utcnow(), pos['pos_huobi'],
#                             "卖出一手huobi", thread_huobi.close)
#                     if pos['pos_okex'] < dic1[key] and pos['pos_okex'] >= 0:
#                         q.put(('buy', 'okex', thread_okex.close, 1))
#                         traded = 1
#                         print(
#                             datetime.utcnow(), pos['pos_okex'],
#                             "买入一手okex", thread_okex.close)
#         if not traded and pos['flag_huobi'] and pos['flag_okex']:
#             if spread < low_cross[0]:
#                 if pos['pos_huobi'] < 0:
#                     q.put(('close', 'huobi', thread_huobi.close, 1))
#                     print(
#                         datetime.utcnow(), pos['pos_huobi'],
#                         "平仓huobi", thread_huobi.close)
#                     traded = 1
#                 if pos['pos_okex'] > 0:
#                     q.put(('close', 'okex', thread_okex.close, 1))
#                     print(
#                         datetime.utcnow(), pos['pos_okex'],
#                         "平仓okex", thread_okex.close)
#                     traded = 1
#             elif spread > high_cross[0]:
#                 if pos['pos_huobi'] > 0:
#                     q.put(('close', 'huobi', thread_huobi.close, 1))
#                     print(
#                         datetime.utcnow(), pos['pos_huobi'],
#                         "平仓huobi", thread_huobi.close)
#                     traded = 1
#                 if pos['pos_okex'] < 0:
#                     q.put(('close', 'okex', thread_okex.close, 1))
#                     print(
#                         datetime.utcnow(), pos['pos_okex'],
#                         "平仓okex", thread_okex.close)
#                     traded = 1
#             # if spread > 8 and spread < 10:
#             #     if pos['pos_okex'] != 0:
#             #         q.put(('close', 'okex', thread_okex.close, 1))
#             #         print(
#             #             datetime.utcnow(), pos['pos_okex'],
#             #             "平仓okex", thread_okex.close)
#             #         traded = 1
#             #     if pos['pos_huobi'] != 0:
#             #         q.put(('close', 'huobi', thread_huobi.close, 1))
#             #         print(
#             #             datetime.utcnow(), pos['pos_huobi'],
#             #             "平仓huobi", thread_huobi.close)
#         if not traded and pos['flag_huobi'] and pos['flag_okex']:
#             dic2 = {low_cross[0]: leverage,
#                     low_cross[1]: 2*leverage,
#                     low_cross[2]: 3*leverage}
#             for key in dic2.keys():
#                 if spread < key and not traded:
#                     if pos['pos_huobi'] < dic2[key] and pos['pos_huobi'] >= 0:
#                         q.put(('buy', 'huobi', thread_huobi.close, 1))
#                         traded = 1
#                         print(
#                             datetime.utcnow(), pos['pos_huobi'],
#                             "买入一手huobi", thread_huobi.close)
#                     if (pos['pos_okex'] > dic2[key]*(-1) and
#                             pos['pos_okex'] <= 0):
#                         q.put(('sell', 'okex', thread_okex.close, 1))
#                         traded = 1
#                         print(
#                             datetime.utcnow(), pos['pos_okex'],
#                             "卖出一手okex", thread_okex.close)
#     elif pos['flag_huobi'] and pos['flag_okex']:
#         print('时间不一致,okex:{},huobi:{}'.format(
#             thread_okex.timestamp, thread_huobi.timestamp))
#         trades[0].init_pos()
#         if not thread_okex.is_alive():
#             print("okex行情线程关闭，重启")
#             thread_okex = P_OKEX('t_okex_{}'.format(SYMBOL_OKEX))
#             thread_okex.ws_okex.send(subStr_okex)
#             thread_okex.start()
#         if not thread_huobi.is_alive():
#             print("huobi行情线程关闭，重启")
#             thread_huobi = P_HUOBI('t_huobi_{}'.format(SYMBOL_HUOBI))
#             thread_huobi.ws_huobi.send(subStr_huobi)
#             thread_huobi.start()
#     time.sleep(2)
