from abc import ABC, abstractmethod


class BaseCandlestick(ABC):

    def __init__(self, base_symbol, quote_symbol, intervals):
        self.base_symbol = base_symbol
        self.quote_symbol = quote_symbol
        self.intervals = intervals
        super().__init__()

    @abstractmethod
    def get_bars(self, numbers):
        pass

    @abstractmethod
    def get_close(self, numbers):
        pass
