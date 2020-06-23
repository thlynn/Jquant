from api.huobi_api.huobi_future_api import HUOBIFutureAPI
from app.run import Run
from app.turtle.turtle_v1 import TurtleV1

from config import Keys
from data.huobi import HUOBIFutureHistory
from data.huobi import SubscribeHUOBIFuture
from monitor.monitor_base import MonitorBase


class TurtleRun(Run):

    def __init__(self, symbol, pos, intervals, contract_type, contract_code, lever_rate):
        super().__init__(symbol, pos, intervals)
        self.contract_type = contract_type
        self.contract_code = contract_code
        self.lever_rate = lever_rate

    def instantiate_strategy(self):
        entry_window = 60
        exit_window = 20
        atr_window = 55

        keys = Keys()

        access_key, secret_key = keys.get_key('HUOBI_FUTRUE')
        base_url = keys.get_base_url('HUOBI_FUTRUE')
        trade_api = HUOBIFutureAPI(
            access_key, secret_key, base_url, self.contract_type, self.contract_code, self.lever_rate)

        strategy = TurtleV1(
            self.symbol, self.pos, entry_window, exit_window, atr_window, trade_api, self.intervals)

        history = self.instantiate_history()
        strategy.init_bars(history.get_bars(2000), self.intervals)

        return strategy

    def instantiate_history(self):
        history = HUOBIFutureHistory(self.symbol, intervals=self.intervals)
        return history

    def start_monitor(self, strategy):
        monitor = MonitorBase(strategy.orders_dict, strategy.on_trade, strategy.trade_api)
        monitor.start()
        return monitor

    def start_subscribe(self, strategy):
        subscribe = SubscribeHUOBIFuture(self.symbol, '1min', callback=strategy.on_bar)
        subscribe.start()
        return subscribe
