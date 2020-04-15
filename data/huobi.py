import json
from decimal import Decimal

import requests

from data.baseCandlestick import BaseCandlestick
from model.BaseModel import Bar


class HUOBIHistory(BaseCandlestick):

    def __init__(self, base_symbol, quote_symbol, intervals='1min'):
        super().__init__(base_symbol, quote_symbol, intervals)
        self.base_url = 'https://api.huobi.pro/market/history/kline'

    def parse_data(self, data):
        bars = list()
        for item in data:
            bar = Bar(
                str.upper(self.base_symbol), str.upper(self.quote_symbol), 'HUOBI', self.intervals, item['id'],
                Decimal(str(item['open'])), Decimal(str(item['high'])),
                Decimal(str(item['low'])), Decimal(str(item['close'])), Decimal(str(item['amount'])))
            bars.append(bar)
        return bars

    def get_data(self, numbers):
        req_str = f'{self.base_url}?period={self.intervals}&size={numbers}&symbol={self.base_symbol}{self.quote_symbol}'
        res = requests.get(req_str)
        data = json.loads(res.content)['data']
        return self.parse_data(data)

