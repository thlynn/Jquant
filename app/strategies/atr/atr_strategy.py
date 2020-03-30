import json
from Jquant.utilities.sub_market_new import P_HUOBI
from Jquant.app.strategies.atr.trader import Trader
from datetime import datetime
from Jquant.app.data.huobi import HuoBiData
import pandas as pd
import talib


class ATRStrategy():

    ATR_RANGE = 14
    MA_ENTRY = 100
    MA_STOP = 10
    # SYMBOL_HUOBI = 'BTC_CQ' 季度  BTC_CW 当周 BTC_NW 次周

    def __init__(self, symbol):
        self.symbol = symbol
        self.pos = 0
        self.trading = 0
        self.leverage = 1
        self.volume = 1
        self.df = None
        self.atr = None
        self.atr_max = None
        self.ma_entry = None
        self.ma_stop = None
        self.hour = None
        self.minute = None
        contract_type = ''
        if symbol == 'BTC_CW':
            contract_type = 'this_week'
        elif symbol == 'BTC_NW':
            contract_type = 'next_week'
        elif symbol == 'BTC_CQ':
            contract_type = 'quarter'
        self.trader = Trader(self.leverage, self.on_trade, contract_type)
        self.long_entry = 0
        self.long_stop = 0
        self.short_entry = 0
        self.short_stop = 0
        self.sub_thread = None

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
        close_price = self.df.iloc[-1].close_price
        stop = max(self.long_stop, self.ma_stop)
        print(datetime.utcnow(),
              'close_price:{}, ma_entry:{}, long_entry:{}, long_stop:{}, ma_stop:{},\
               atr:{}, atr_max:{}'.format(
               close_price, self.ma_entry, self.long_entry, self.long_stop,
               self.ma_stop, self.atr, self.atr_max))
        if self.trading == 0:
            if (not self.pos and self.atr == self.atr_max and
                    close_price >= self.ma_entry):
                self.trader.buy(self.volume, close_price, 'limit')
                self.trading = 1
            elif (self.pos > 0 and self.pos < 4 and
                  close_price >= self.long_entry):
                self.trader.buy(self.volume, close_price, 'limit')
                self.trading = 1
            elif self.pos and close_price <= stop:
                self.trader.close(self.pos, 'sell', close_price, 'limit')
                self.trading = 1
        else:
            self.trader.cancel_order()

    def on_trade(self, tradeInfo):
        if tradeInfo.trade_volume:
            if tradeInfo.direction == "buy":
                self.pos += tradeInfo.trade_volume
                if tradeInfo.offset == "open":
                    self.long_entry = tradeInfo.price_avg + 0.5 * self.atr
                    self.long_stop = tradeInfo.price_avg - 2 * self.atr
            else:
                self.pos -= tradeInfo.trade_volume
                if tradeInfo.offset == "open":
                    self.short_entry = tradeInfo.price_avg - 0.5 * self.atr
                    self.short_stop = tradeInfo.price_avg + 2 * self.atr
        else:
            self.on_bar()
        self.trading = 0

    # def init_parameters(self):
    #     df_60 = self.df.resample(
    #         '60min', closed='left', label='right').agg(
    #         {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
    #     atr = talib.ATR(df_60.high, df_60.low, df_60.close, 14)
    #     df_60 = df_60.assign(atr=atr)
    #     ma = talib.SMA(df_60.close, 100)
    #     df_60 = df_60.assign(ma=ma)
    #     self.ma = df_60.iloc[-2].ma
    #     self.atr = df_60.iloc[-2].atr

    def init_parameters(self):
        df = self.df
        atr = talib.ATR(
            df.high_price, df.low_price, df.close_price, self.ATR_RANGE)
        df = df.assign(atr=atr)
        ma_entry = talib.SMA(df.close_price, self.MA_ENTRY)
        df = df.assign(ma_entry=ma_entry)
        ma_stop = talib.SMA(df.close_price, self.MA_STOP)
        df = df.assign(ma_stop=ma_stop)
        self.ma_entry = df.iloc[-2].ma_entry
        self.ma_stop = df.iloc[-2].ma_stop
        self.atr = df.iloc[-2].atr
        self.atr_max = df.atr[-1-self.ATR_RANGE:-1].max()

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
            # if self.hour != date.hour:
            #     self.hour = date.hour
            #     self.init_parameters()
            if self.minute != date.minute:
                self.minute = date.minute
                self.init_parameters()
                if not self.trading:
                    self.on_bar()


if __name__ == '__main__':
    atr = ATRStrategy('BTC_CQ')
    atr.start_strategy()
