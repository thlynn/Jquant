import json
from decimal import Decimal

import requests

from core.exceptions import APIError
from core.logger import get_logger
from data.candlesticks import BaseCandlestick
from model.BaseModel import Bar

import gzip

from websocket import create_connection

from app.base_strategy import BaseStrategy
from data.subscribe import Subscribe


class HUOBIHistory(BaseCandlestick):

    def __init__(self, symbol, intervals='1min'):
        super().__init__(symbol, intervals)
        self.base_url = 'https://api.huobi.pro/market/history/kline'
        self.response_data = None

    def get_bars(self, numbers, begin=None, end=None):
        if not self.response_data:
            self.req_data(numbers, begin, end)
        bars = list()
        for item in self.response_data:
            bar = Bar(
                str.upper(self.symbol), 'HUOBI', self.intervals, item['id'],
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
        req_str = f'{self.base_url}?period={self.intervals}&size={numbers}&symbol={self.symbol}'
        res = requests.get(req_str)
        result = json.loads(res.content)
        if result['status'] == 'error':
            raise APIError(result['err-msg'])
        self.response_data = json.loads(res.content)['data']


class HUOBIFutureHistory(BaseCandlestick):

    def __init__(self, symbol, future_type='CQ', intervals='1min'):
        super().__init__(symbol, intervals)
        self.base_url = 'https://api.hbdm.com/market/history/kline'
        self.future_type = future_type

    def get_bars(self, numbers):
        response_data = self.req_data(numbers)
        return self.construct(response_data)

    def construct(self, response_data):
        return_bars = list()
        for item in response_data:
            bar = Bar(
                str.upper(self.symbol), 'HUOBI', self.intervals, item['id'],
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
        req_str = f'{self.base_url}?period={self.intervals}&size={numbers}&symbol={str.upper(self.symbol)}_{str.upper(self.future_type)}'
        res = requests.get(req_str)
        result = json.loads(res.content)
        if result['status'] == 'error':
            raise APIError(result['err-msg'])
        return result['data']

    def req_data_by_time_range(self, begin_time, end_time):
        req_str = f'{self.base_url}?period={self.intervals}&from={begin_time}&to={end_time}&symbol={str.upper(self.symbol)}_{str.upper(self.future_type)}'
        res = requests.get(req_str)
        result = json.loads(res.content)
        if result['status'] == 'error':
            raise APIError(result['err-msg'])
        return result['data']


class SubscribeHUOBIFuture(Subscribe):

    def __init__(self, symbol, intervals, future_type='CQ', callback=None):
        super().__init__(symbol, intervals, callback)
        self.ws_url = "wss://www.hbdm.com/ws"
        self.future_type = future_type
        self.logger = get_logger('subscribe')

    def run(self):
        ws = None
        while not ws:
            try:
                ws = create_connection(self.ws_url)
            except Exception as e:
                self.logger.error(e)
        topic = {
            "sub": f"market.{str.upper(self.symbol)}_{str.upper(self.future_type)}.kline.{self.intervals}",
            "id": "id1"
        }
        ws.send(json.dumps(topic))

        while True:
            result = gzip.decompress(ws.recv()).decode('utf-8')
            json_obj = json.loads(result)
            if json_obj.get('status') == 'error':
                pass
            elif 'ping' in json_obj.keys():
                pong = '{"pong":'+str(json_obj['ping'])+'}'
                ws.send(pong)
            elif 'ch' in json_obj.keys():
                tick = json_obj['tick']

                self.timestamp = int(tick['id'])
                self.open = Decimal(str(tick['open']))
                self.close = Decimal(str(tick['close']))
                self.low = Decimal(str(tick['low']))
                self.high = Decimal(str(tick['high']))
                self.amount = Decimal(str(tick['amount']))

                self.logger.debug(f'timestamp: {self.timestamp}, close: {self.close}')

                if self.callback:
                    bar = Bar(
                        self.symbol, self.name, self.intervals,
                        self.timestamp, self.open, self.high, self.low, self.close, self.amount)
                    self.callback(bar)


class SubscribeHUOBI(Subscribe):

    def __init__(self, symbol, intervals, callback=None):
        super().__init__(symbol, intervals, callback)
        self.ws_url = "wss://api.huobi.pro/ws"

    def run(self):
        topic = {
            "sub": f"market.{str.lower(self.symbol)}.kline.{self.intervals}",
            "id": "id1"
        }
        ws = create_connection("wss://api.huobi.pro/ws")
        ws.send(json.dumps(topic))

        while True:
            result = gzip.decompress(ws.recv()).decode('utf-8')
            json_obj = json.loads(result)

            if json_obj.get('status') == 'error':
                pass
            elif 'ping' in json_obj.keys():
                pong = '{"pong":'+str(json_obj['ping'])+'}'
                ws.send(pong)
            elif 'ch' in json_obj.keys():
                tick = json_obj['tick']
                self.timestamp = int(tick['id'])
                self.open = Decimal(str(tick['open']))
                self.close = Decimal(str(tick['close']))
                self.low = Decimal(str(tick['low']))
                self.high = Decimal(str(tick['high']))
                self.amount = Decimal(str(tick['amount']))

                if self.callback:
                    bar = Bar(
                        self.symbol, self.name, self.intervals,
                        self.timestamp, self.open, self.high, self.low, self.close, self.amount)
                    self.callback(bar)


class SubscribeHUOBIFutureBackTest(Subscribe):

    def __init__(self, symbol, intervals, strategy:BaseStrategy, api_callback):
        super().__init__(symbol, intervals, strategy.on_bar)
        self.api_callback = api_callback

    def run_backtest(self, back_test_bars, monitor):
        for index, bar in back_test_bars.iterrows():
            if self.callback:
                bar = Bar(
                    self.symbol, 'HUOBI', self.intervals,
                    bar.timestamp, Decimal(str(bar.open_price)), Decimal(str(bar.high_price)),
                    Decimal(str(bar.low_price)), Decimal(str(bar.close_price)), bar.amount)

                self.callback(bar)

                self.api_callback(bar)

                monitor.monitor_order()
