from decimal import Decimal

from data.candlesticks import BaseCandlestick
from model.BaseModel import Bar


class BithumbCandlestick(BaseCandlestick):

    def get_close(self, numbers, begin=None, end=None):
        pass

    def get_bars(self, numbers, begin=None, end=None):
        pass

    def __init__(self, base_symbol, quote_symbol, intervals='1m'):
        super().__init__(base_symbol, quote_symbol, intervals)
        base_url = 'https://api.bithumb.com/public/candlestick'
        self.req_str = f'{base_url}/{self.base_symbol}_{self.quote_symbol}/{self.intervals}'

    def parse_data(self, data):
        for item in data:
            symbol = f'{self.base_symbol}_{self.quote_symbol}'
            bar = Bar(
                symbol, 'bithumb', self.intervals, item[0]*0.001,
                Decimal(item[1]), Decimal(item[3]), Decimal(item[4]), Decimal(item[2]), Decimal(item[5]))
            self.bars.append(bar)

