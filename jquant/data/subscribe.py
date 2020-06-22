import threading
from decimal import Decimal

from core.logger import get_logger


class Subscribe(threading.Thread):

    def __init__(self, base_symbol, quote_symbol, intervals, callback=None):
        super().__init__()
        self.base_symbol = base_symbol
        self.quote_symbol = quote_symbol
        self.timestamp = float
        self.open: Decimal = Decimal('0')
        self.close: Decimal = Decimal('0')
        self.low: Decimal = Decimal('0')
        self.high: Decimal = Decimal('0')
        self.amount = Decimal('0')
        self.callback = callback
        self.intervals = intervals

        self.logger = get_logger('subscribe')





