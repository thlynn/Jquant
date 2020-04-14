import json
from Jquant.utilities.sub_market_new import P_HUOBI
from Jquant.utilities.tools import donchian, atr
from Jquant.app.strategies.turtle.trader import Trader
from Jquant.model.BaseModel import Order
from datetime import datetime
from Jquant.app.data.huobi import HuoBiData
import pandas as pd
import configparser
import os


class TurtleStrategy():

    entry_window = 55
    exit_window = 20
    atr_window = 20
    # SYMBOL_HUOBI = 'BTC_CQ' 季度  BTC_CW 当周 BTC_NW 次周

    def __init__(self, symbol):
        self.symbol = symbol
        self.pos = 0
        self.leverage = 1
        self.volume = 1
        self.df = None

        self.trading = 0

        self.atr_value = None
        self.entry_up = None
        self.entry_down = None
        self.exit_up = None
        self.exit_down = None

        self.minute = None
        self.hour = None
        contract_type = ''
        if symbol == 'BTC_CW':
            contract_type = 'this_week'
        elif symbol == 'BTC_NW':
            contract_type = 'next_week'
        elif symbol == 'BTC_CQ':
            contract_type = 'quarter'
        self.trader = Trader(self.leverage, self.on_trade, contract_type)
        self.load_parameters()
        # 行情线程
        self.sub_thread = None
        self.stop_orders = list()

    def load_parameters(self):
        config = configparser.ConfigParser()
        config.read(os.path.dirname(__file__) + '/turtle.ini')
        self.long_entry = float(config['param']['long_entry'])
        self.long_stop = float(config['param']['long_stop'])
        self.short_entry = float(config['param']['short_entry'])
        self.short_stop = float(config['param']['short_stop'])

    def save_parameters(self):
        config = configparser.ConfigParser()
        config['param'] = {}
        config['param']['long_entry'] = str(self.long_entry)
        config['param']['long_stop'] = str(self.long_stop)
        config['param']['short_entry'] = str(self.short_entry)
        config['param']['short_stop'] = str(self.short_stop)
        with open(os.path.dirname(__file__) + '/turtle.ini', 'w') as f:
            config.write(f)

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
        begin = end - 120*60*60
        bars = huobiData.ws_data('BTC_CQ', '1min', begin, end)
        self.df = pd.DataFrame(data=bars)
        self.df = self.df.drop_duplicates()
        self.df['datetime'] = self.df['timestamp'].apply(
            lambda x: datetime.fromtimestamp(x))
        self.df.set_index('datetime', inplace=True)
        self.df = self.df[
            ['open_price', 'close_price', 'high_price', 'low_price']]

    def on_bar(self):
        if self.trading == 0:
            close_price = self.df.iloc[-1].close_price
            print(datetime.utcnow(),
                  '''close_price:{}, atr_value:{}
                   entry_up:{}, long_entry:{}, exit_down:{}, long_stop:{}
                   entry_down:{}, short_entry:{}, exit_up:{}, short_stop:{}
                   '''.format(
                   close_price, self.atr_value,
                   self.entry_up, self.long_entry,
                   self.exit_down, self.long_stop,
                   self.entry_down, self.short_entry,
                   self.exit_up, self.short_stop
                   ))
            if not self.pos:
                # 在突破价格，多头或空头开仓
                self.transaction(
                    self.volume, 'buy', 'open', self.entry_up, 'limit')
                self.transaction(
                    self.volume, 'sell', 'open', self.entry_down, 'limit')
                self.trading = 1
            # 多头头寸规模最大为4
            elif self.pos > 0 and self.pos <= 4:
                if self.pos < 4:
                    self.transaction(
                        self.volume, 'buy', 'open', self.long_entry, 'limit')
                # 止损或者退出全部头寸
                sell_price = max(self.long_stop, self.exit_down)
                self.transaction(abs(self.pos), 'sell', 'close', sell_price)
                self.trading = 1
            # 空头头寸规模最大为4
            elif self.pos < 0 and self.pos >= -4:
                if self.pos > -4:
                    self.transaction(
                        self.volume, 'sell', 'open', self.short_entry, 'limit')
                cover_price = min(self.short_stop, self.exit_up)
                self.transaction(abs(self.pos), 'buy', 'close', cover_price)
                self.trading = 1
            print(self.stop_orders)

    def on_trade(self, tradeInfo):
        if tradeInfo.trade_volume:
            if tradeInfo.direction == "buy":
                self.pos += tradeInfo.trade_volume
                if tradeInfo.offset == "open":
                    self.long_entry = (tradeInfo.price_avg +
                                       0.5 * self.atr_value)
                    self.long_stop = (tradeInfo.price_avg -
                                      2 * self.atr_value)
            else:
                self.pos -= tradeInfo.trade_volume
                if tradeInfo.offset == "open":
                    self.short_entry = (tradeInfo.price_avg -
                                        0.5 * self.atr_value)
                    self.short_stop = tradeInfo.price_avg + 2 * self.atr_value
        self.save_parameters()
        self.cancel_all()

    def init_parameters(self):
        df_60 = self.df.resample(
            '60min', closed='left', label='right').agg(
            {'open_price': 'first', 'high_price': 'max',
             'low_price': 'min', 'close_price': 'last'})
        # 入市
        self.entry_up, self.entry_down = donchian(self.entry_window, df_60)
        # 退出
        self.exit_up, self.exit_down = donchian(self.exit_window, df_60)
        # 真实波动幅度均值
        self.atr_value = atr(self.atr_window, df_60)
        self.cancel_all()

    def start_strategy(self):
        self.pos = self.trader.init_pos()
        print("初始头寸:{}".format(self.pos))
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
            if self.hour != date.hour:
                self.hour = date.hour
                self.init_parameters()
            if self.minute != date.minute:
                self.minute = date.minute
                self.on_bar()
            self.send_order(tick['close_price'])

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
            datetime.utcnow(), '下停止单',
            direction, offset, price, volume, orderType)
        order = Order(direction, offset, price, volume, orderType)
        self.stop_orders.append(order)

    def cancel_all(self):
        self.stop_orders.clear()
        self.trader.cancel_all()
        self.trading = 0


if __name__ == '__main__':
    turtle = TurtleStrategy('BTC_CQ')
    turtle.start_strategy()
