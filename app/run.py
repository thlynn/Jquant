import time
from abc import ABC, abstractmethod


class Run(ABC):

    def __init__(self, base_symbol, quote_symbol, pos, intervals):
        self.base_symbol = base_symbol
        self.quote_symbol = quote_symbol
        self.pos = pos
        self.intervals = intervals

    def proceed(self):
        strategy = self.instantiate_strategy()

        history = self.instantiate_history()

        strategy.init_bars(history.get_bars(1000))

        monitor = None
        subscribe = None

        while True:
            if not monitor or not monitor.is_alive():
                monitor = self.start_monitor(strategy)
            if not subscribe or not subscribe.is_alive():
                subscribe = self.start_subscribe(strategy)
            time.sleep(5)

    @abstractmethod
    def instantiate_strategy(self):
        pass

    @abstractmethod
    def instantiate_history(self):
        pass

    @abstractmethod
    def start_monitor(self, strategy):
        pass

    @abstractmethod
    def start_subscribe(self, strategy):
        pass
