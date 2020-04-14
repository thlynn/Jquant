import json
from Jquant.utilities.sub_market_new import P_HUOBI
from Jquant.app.strategies.turtle.trader import Trader
from datetime import datetime
from Jquant.app.data.huobi import HuoBiData
import pandas as pd
import talib


class MAStrategy():

    MA_S = 5
    MA_B = 10

    def __init__(self, symbol):
        self.symbol = symbol
        self.pos_positive = 0
        self.pos_negative = 0
        self.leverage = 1
        self.volume = 1
        self.df = None
        self.minute = None
        self.trend = None
        contract_type = ''
        if symbol == 'BTC_CW':
            contract_type = 'this_week'
        elif symbol == 'BTC_NW':
            contract_type = 'next_week'
        elif symbol == 'BTC_CQ':
            contract_type = 'quarter'
        self.trader = Trader(self.leverage, self.on_trade, contract_type)
        # 行情线程
        self.sub_thread = None
        self.stop_orders = list()

    def sub_market(self):
        subscribe = "market.{}.kline.{}".format(self.symbol, '1min')
        subStr = json.dumps({"sub": subscribe, "id": "id1"})
        self.sub_thread = P_HUOBI(
            't_huobi_{}'.format(self.symbol), self.on_sub)
        self.sub_thread.ws_huobi.send(subStr)
        self.sub_thread.start()
        self.sub_thread.join()

    def load_data(self):
        # 初始化策略参数
        huobiData = HuoBiData()
        now = datetime.now()
        end = int(datetime.timestamp(now) - now.second)
        begin = end - 60*60
        bars = huobiData.ws_data('BTC_CQ', '1min', begin, end)
        self.df = pd.DataFrame(data=bars)
        self.df = self.df.drop_duplicates()
        self.df['datetime'] = self.df['timestamp'].apply(
            lambda x: datetime.fromtimestamp(x))
        self.df.set_index('datetime', inplace=True)
        self.df = self.df[
            ['open_price', 'close_price', 'high_price', 'low_price']]

    def on_bar(self):
        close_price = self.df.iloc[-1].close_price
        flag = 0
        if self.ma_s > self.ma_b:
            ctrend = 'top'
        elif self.ma_s < self.ma_b:
            ctrend = 'bottom'
        if not self.trend:
            self.trend = ctrend
        elif self.trend == ctrend:
            if ((ctrend == 'top' and self.pos_negative > 0) or
                    (ctrend == 'bottom' and self.pos_positive > 0)):
                self.cancel_all()
                flag = 1
        if self.trend != ctrend or flag:
            self.trend = ctrend
            if ctrend == 'top':
                if not self.pos_positive:
                    self.transaction(
                        self.volume, 'buy', 'open', close_price, 'limit')
                if self.pos_negative:
                    self.transaction(
                        abs(self.pos_negative), 'buy',
                        'close', close_price, 'limit')
            elif ctrend == 'bottom':
                if not self.pos_negative:
                    self.transaction(
                        self.volume, 'sell', 'open', close_price, 'limit')
                if self.pos_positive:
                    self.transaction(
                        abs(self.pos_positive), 'sell', 'close',
                        close_price, 'limit')
        # print(self.stop_orders)

    def caculate_parameters(self):
        df = self.df
        ma_s = talib.SMA(df.close_price, self.MA_S)
        df = df.assign(ma_s=ma_s)
        ma_b = talib.SMA(df.close_price, self.MA_B)
        df = df.assign(ma_b=ma_b)
        self.ma_s = df.iloc[-2].ma_s
        self.ma_b = df.iloc[-2].ma_b

    def on_trade(self, tradeInfo):
        if tradeInfo.trade_volume:
            if tradeInfo.offset == 'open':
                if tradeInfo.direction == "buy":
                    self.pos_positive += tradeInfo.trade_volume
                else:
                    self.pos_negative += tradeInfo.trade_volume
            elif tradeInfo.offset == 'close':
                if tradeInfo.direction == "buy":
                    self.pos_negative -= tradeInfo.trade_volume
                else:
                    self.pos_positive -= tradeInfo.trade_volume
        print('pos_positive:{},pos_negative:{}'.format(
            self.pos_positive, self.pos_negative))

    def start_strategy(self):
        self.load_data()
        self.sub_market()
        while not self.sub_thread.is_alive():
            print("huobi行情线程关闭，重启")
            self.sub_market()

    def on_sub(self, obj):
        # 回调函数
        if type(self.df) == pd.DataFrame and not self.df.empty:
            tick = obj.__dict__
            date = datetime.fromtimestamp(obj.timestamp)
            tick.pop('timestamp')
            tick.pop('volume')
            self.df.loc[date] = tick
            if len(self.df.index) > 10000:
                self.df = self.df.sort_index()
                self.df = self.df[-10000:]
            if self.minute != date.minute:
                self.minute = date.minute
                self.caculate_parameters()
                self.on_bar()
            # self.send_order(tick['close_price'])

    def send_order(self, closePrice):
        for order in self.stop_orders:
            if ((order.direction == 'buy' and closePrice >= order.price) or
                    (order.direction == 'sell' and closePrice <= order.price)):
                print(
                    datetime.utcnow(), '下单',
                    order.volume, order.direction, order.offset,
                    order.price, order.type)
                self.trader.transaction(
                    order.volume, order.direction, order.offset,
                    order.price, order.type)
                self.stop_orders.remove(order)

    def transaction(
            self, volume, direction, offset, price=None, orderType='opponent'):
        print(
            datetime.utcnow(), '下限价单',
            direction, offset, price, volume, orderType)
        if volume:
            self.trader.transaction(
                volume, direction, offset, price, orderType)
        # order = Order(direction, offset, price, volume, orderType)
        # self.stop_orders.append(order)

    def cancel_all(self):
        self.stop_orders.clear()
        self.trader.cancel_all()


if __name__ == '__main__':
    turtle = MAStrategy('BTC_CQ')
    turtle.start_strategy()
