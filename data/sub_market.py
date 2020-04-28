import threading
import gzip
import json
import time
from decimal import Decimal

import requests
from websocket import create_connection
from datetime import datetime

from core.logger import get_logger
from data.tools import inflate
from model.BaseModel import Bar


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

                self.logger.debug(f'{bar.timestamp},{bar.close_price}')

                if self.callback:
                    bar = Bar(
                        self.base_symbol, self.quote_symbol, self.name, self.intervals,
                        self.timestamp, self.open, self.high, self.low, self.close, self.amount)
                    self.callback(bar)


class SubscribeEXMO(Subscribe):

    def __init__(self, base_symbol, quote_symbol):
        super().__init__(base_symbol, quote_symbol)
        self.ticker_url = "https://api.exmo.com/v1/ticker/"

    def run(self):
        while True:
            time.sleep(0.5)
            try:
                res = requests.get(self.ticker_url, timeout=5)
            except IOError:
                continue
            ticker = json.loads(res.content)[f'{str.upper(self.base_symbol)}_{str.upper(self.quote_symbol)}']
            updated = ticker['updated']

            self.timestamp = updated
            self.close = Decimal(str(ticker['last_trade']))


class SubscribeOKEXFuture(Subscribe):

    def __init__(self, base_symbol, quote_symbol, intervals, callback=None):
        super().__init__(base_symbol, quote_symbol, intervals, callback)
        self.ws_url = create_connection("wss://real.okex.com:8443/ws/v3")

    def run(self):
        while True:
            result = inflate(self.ws_url.recv())
            if result == b'pong':
                pass
            else:
                json_obj = json.loads(result)
                if 'data' in json_obj.keys():
                    data = json_obj['data'][0]
                    candle = data['candle']
                    timestamp = datetime.strptime(
                        candle[0], '%Y-%m-%dT%H:%M:%S.%fZ')
                    self.timestamp = timestamp
                    if candle[4]:
                        self.close = float(candle[4])
                    if (not self.timestamp or
                            self.timestamp.minute != timestamp.minute):
                        self.ws_url.send('ping')
