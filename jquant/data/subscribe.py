import threading
from decimal import Decimal


class Subscribe(threading.Thread):

    def __init__(self, symbol, intervals, callback=None):
        super().__init__()
        self.symbol = symbol
        self.timestamp = float
        self.open: Decimal = Decimal('0')
        self.close: Decimal = Decimal('0')
        self.low: Decimal = Decimal('0')
        self.high: Decimal = Decimal('0')
        self.amount = Decimal('0')
        self.callback = callback
        self.intervals = intervals





