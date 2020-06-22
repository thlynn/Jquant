from abc import ABC, abstractmethod


class BaseCandlestick(ABC):

    def __init__(self, symbol, intervals):
        self.symbol = symbol
        self.intervals = intervals
        super().__init__()

    @abstractmethod
    def get_bars(self, numbers):
        pass

    @abstractmethod
    def get_close(self, numbers):
        pass
