import json
from abc import ABC, abstractmethod
from decimal import Decimal

import requests

from core.exceptions import APIError
from model.BaseModel import Bar, EnhancedJSONEncoder


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

    def to_json(self):
        return json.dumps(self.bars, cls=EnhancedJSONEncoder)


class HUOBIHistory(BaseCandlestick):

    def __init__(self, base_symbol, quote_symbol, intervals='1min'):
        super().__init__(base_symbol, quote_symbol, intervals)
        self.base_url = 'https://api.huobi.pro/market/history/kline'
        self.response_data = None

    def get_bars(self, numbers):
        if not self.response_data:
            self.req_data(numbers)
        bars = list()
        for item in self.response_data:
            bar = Bar(
                str.upper(self.base_symbol), str.upper(self.quote_symbol), 'HUOBI', self.intervals, item['id'],
                Decimal(str(item['open'])), Decimal(str(item['high'])),
                Decimal(str(item['low'])), Decimal(str(item['close'])), Decimal(str(item['amount'])))
            bars.append(bar)
        return bars

    def get_close(self, numbers):
        if not self.response_data:
            self.req_data(numbers)
        close_prices = list()
        for item in self.response_data:
            close_prices.append(Decimal(str(item['close'])))
        return close_prices

    def req_data(self, numbers):
        req_str = f'{self.base_url}?period={self.intervals}&size={numbers}&symbol={self.base_symbol}{self.quote_symbol}'
        res = requests.get(req_str)
        result = json.loads(res.content)
        if result['status'] == 'error':
            raise APIError(result['err-msg'])
        self.response_data = json.loads(res.content)['data']


class HUOBIFutureHistory(BaseCandlestick):

    def __init__(self, base_symbol, quote_symbol, future_type='CQ', intervals='1min'):
        super().__init__(base_symbol, quote_symbol, intervals)
        self.base_url = 'https://api.hbdm.com/market/history/kline'
        self.response_data = None
        self.future_type = future_type

    def get_bars(self, numbers):
        if not self.response_data:
            self.req_data(numbers)
        bars = list()
        for item in self.response_data:
            bar = Bar(
                str.upper(self.base_symbol), str.upper(self.quote_symbol), 'HUOBI', self.intervals, item['id'],
                Decimal(str(item['open'])), Decimal(str(item['high'])),
                Decimal(str(item['low'])), Decimal(str(item['close'])), Decimal(str(item['amount'])))
            bars.append(bar)
        return bars

    def get_close(self, numbers):
        if not self.response_data:
            self.req_data(numbers)
        close_prices = list()
        for item in self.response_data:
            close_prices.append(Decimal(str(item['close'])))
        return close_prices

    def req_data(self, numbers):
        req_str = f'{self.base_url}?period={self.intervals}&size={numbers}&symbol={str.upper(self.base_symbol)}_{str.upper(self.future_type)}'
        res = requests.get(req_str)
        result = json.loads(res.content)
        if result['status'] == 'error':
            raise APIError(result['err-msg'])
        self.response_data = result['data']

