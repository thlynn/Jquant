from app.run import Run
from app.turtle.turtle_v1 import TurtleV1
from back_test.back_test_api import BackTestAPI
from data.huobi import SubscribeHUOBIFutureBackTest

from monitor.monitor_base import MonitorBase

import pandas as pd


class TurtleRunBackTest(Run):

    def __init__(self, symbol, pos, intervals, entry_window, exit_window, atr_window, init_bars):
        super().__init__(symbol, pos, intervals)
        self.entry_window = entry_window
        self.exit_window = exit_window
        self.atr_window = atr_window
        self.init_bars = init_bars

    def instantiate_strategy(self):

        trade_api = BackTestAPI()
        strategy = TurtleV1(
            self.symbol, self.pos, self.entry_window, self.exit_window, self.atr_window, trade_api, self.intervals)

        strategy.init_bars([row for index, row in self.init_bars.iterrows()], self.intervals)

        return strategy

    def proceed_back_test(self, back_test_bars):
        strategy = self.instantiate_strategy()
        monitor = self.start_monitor(strategy)
        subscribe = self.start_subscribe(strategy)

        subscribe.run_backtest(back_test_bars, monitor)

        df = pd.DataFrame(strategy.trade_api.orders)
        df['cum'] = df.account.cumsum()

        return df

    def instantiate_history(self):
        pass

    def start_monitor(self, strategy):
        monitor = MonitorBase(strategy.orders_dict, strategy.on_trade, strategy.trade_api)
        return monitor

    def start_subscribe(self, strategy):
        subscribe = SubscribeHUOBIFutureBackTest(
            self.symbol, '1min', strategy, api_callback=strategy.trade_api.on_bar)
        return subscribe
