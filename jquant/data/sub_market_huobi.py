import gzip
import json
from decimal import Decimal

from websocket import create_connection

from app.base_strategy import BaseStrategy
from data.sub_market import Subscribe
from model.BaseModel import Bar


class SubscribeHUOBIFuture(Subscribe):

    def __init__(self, base_symbol, quote_symbol, intervals, future_type='CQ', callback=None):
        super().__init__(base_symbol, quote_symbol, intervals, callback)
        self.ws_url = "wss://www.hbdm.com/ws"
        self.future_type = future_type

    def run(self):
        ws = None
        while not ws:
            try:
                ws = create_connection(self.ws_url)
            except Exception as e:
                self.logger.error(e)
        topic = {
            "sub": f"market.{str.upper(self.base_symbol)}_{str.upper(self.future_type)}.kline.{self.intervals}",
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

                if self.callback:
                    bar = Bar(
                        self.base_symbol, self.quote_symbol, self.name, self.intervals,
                        self.timestamp, self.open, self.high, self.low, self.close, self.amount)
                    self.logger.debug(f'{bar.timestamp},{bar.close_price}')
                    self.callback(bar)


class SubscribeHUOBI(Subscribe):

    def __init__(self, base_symbol, quote_symbol, intervals, callback=None):
        super().__init__(base_symbol, quote_symbol, intervals, callback)
        self.ws_url = "wss://api.huobi.pro/ws"

    def run(self):
        topic = {
            "sub": f"market.{str.lower(self.base_symbol)}{str.lower(self.quote_symbol)}.kline.{self.intervals}",
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
                        self.base_symbol, self.quote_symbol, self.name, self.intervals,
                        self.timestamp, self.open, self.high, self.low, self.close, self.amount)
                    self.callback(bar)


class SubscribeHUOBIFutureBackTest(Subscribe):

    def __init__(
            self, base_symbol, quote_symbol, intervals,
            back_test_bars, monitor, strategy:BaseStrategy, api_callback):
        super().__init__(base_symbol, quote_symbol, intervals, strategy.on_bar)
        self.back_test_bars = back_test_bars
        self.monitor = monitor
        self.api_callback = api_callback

    def run(self):
        for index, bar in self.back_test_bars.iterrows():
            if self.callback:
                bar = Bar(
                    self.base_symbol, self.quote_symbol, 'HUOBI', self.intervals,
                    bar.timestamp, bar.open_price, bar.high_price, bar.low_price, bar.close_price, bar.amount)

                self.callback(bar)

                self.api_callback(bar)

                self.monitor.monitor_order()
