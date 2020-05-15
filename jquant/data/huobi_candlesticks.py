import json
from decimal import Decimal

import requests

from core.exceptions import APIError
from data.candlesticks import BaseCandlestick
from jquant.model.BaseModel import Bar


class HUOBIHistory(BaseCandlestick):

    def __init__(self, base_symbol, quote_symbol, intervals='1min'):
        super().__init__(base_symbol, quote_symbol, intervals)
        self.base_url = 'https://api.huobi.pro/market/history/kline'
        self.response_data = None

    def get_bars(self, numbers, begin=None, end=None):
        if not self.response_data:
            self.req_data(numbers, begin, end)
        bars = list()
        for item in self.response_data:
            bar = Bar(
                str.upper(self.base_symbol), str.upper(self.quote_symbol), 'HUOBI', self.intervals, item['id'],
                Decimal(str(item['open'])), Decimal(str(item['high'])),
                Decimal(str(item['low'])), Decimal(str(item['close'])), Decimal(str(item['amount'])))
            bars.append(bar)
        return bars

    def get_close(self, numbers, begin=None, end=None):
        if not self.response_data:
            self.req_data(numbers)
        close_prices = list()
        for item in self.response_data:
            close_prices.append(Decimal(str(item['close'])))
        return close_prices

    def req_data(self, numbers, begin=None, end=None):
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
        self.future_type = future_type

    def get_bars(self, numbers):
        response_data = self.req_data(numbers)
        return self.construct(response_data)

    def construct(self, response_data):
        return_bars = list()
        for item in response_data:
            bar = Bar(
                str.upper(self.base_symbol), str.upper(self.quote_symbol), 'HUOBI', self.intervals, item['id'],
                Decimal(str(item['open'])), Decimal(str(item['high'])),
                Decimal(str(item['low'])), Decimal(str(item['close'])), Decimal(str(item['amount'])))
            return_bars.append(bar)
        return return_bars

    def get_close(self, numbers):
        response_data = self.req_data(numbers)
        close_prices = list()
        for item in response_data:
            close_prices.append(Decimal(str(item['close'])))
        return close_prices

    def req_data(self, numbers):
        req_str = f'{self.base_url}?period={self.intervals}&size={numbers}&symbol={str.upper(self.base_symbol)}_{str.upper(self.future_type)}'
        res = requests.get(req_str)
        result = json.loads(res.content)
        if result['status'] == 'error':
            raise APIError(result['err-msg'])
        return result['data']

    def req_data_by_time_range(self, begin_time, end_time):
        req_str = f'{self.base_url}?period={self.intervals}&from={begin_time}&to={end_time}&symbol={str.upper(self.base_symbol)}_{str.upper(self.future_type)}'
        res = requests.get(req_str)
        result = json.loads(res.content)
        if result['status'] == 'error':
            raise APIError(result['err-msg'])
        return result['data']
