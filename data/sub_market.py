import threading
import gzip
import json
import time
from decimal import Decimal

import requests
from websocket import create_connection
from datetime import datetime

from data.tools import inflate


class SubscribeOKEXFuture(threading.Thread):

    def __init__(self, name):
        super().__init__(name=name)
        self.timestamp = None
        self.close = None
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


class SubscribeHUOBIFuture(threading.Thread):

    def __init__(self, name):
        super().__init__(name=name)
        self.timestamp = None
        self.close: Decimal = None
        self.ws_url = create_connection("wss://www.hbdm.com/ws")

    def run(self):
        while True:
            result = gzip.decompress(self.ws_url.recv()).decode('utf-8')
            json_obj = json.loads(result)
            if json_obj.get('status') == 'error':
                pass
            elif 'ping' in json_obj.keys():
                pong = '{"pong":'+str(json_obj['ping'])+'}'
                self.ws_url.send(pong)
            elif 'ch' in json_obj.keys():
                tick = json_obj['tick']
                timestamp = datetime.utcfromtimestamp(
                    tick['id'])
                self.timestamp = timestamp
                self.close = tick['close']


class Subscribe(threading.Thread):

    def __init__(self, base_symbol, quote_symbol, name, callback=None):
        super().__init__(name=name)
        self.base_symbol = base_symbol
        self.quote_symbol = quote_symbol
        self.timestamp = float
        self.open: Decimal = Decimal('0')
        self.close: Decimal = Decimal('0')
        self.low: Decimal = Decimal('0')
        self.high: Decimal = Decimal('0')
        self.amount = Decimal('0')
        self.callback = callback


class SubscribeHUOBI(Subscribe):

    def __init__(self, base_symbol, quote_symbol, name='HUOBI', callback=None):
        super().__init__(base_symbol, quote_symbol, name, callback)
        self.ws_url = "wss://api.huobi.pro/ws"

    def run(self):
        topic = {
            "sub": f"market.{str.lower(self.base_symbol)}{str.lower(self.quote_symbol)}.kline.1min",
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
                self.timestamp = tick['id']
                self.open = Decimal(str(tick['open']))
                self.close = Decimal(str(tick['close']))
                self.low = Decimal(str(tick['low']))
                self.high = Decimal(str(tick['high']))
                self.amount = Decimal(str(tick['amount']))

                if self.callback:
                    self.callback()


class SubscribeEXMO(Subscribe):

    def __init__(self, base_symbol, quote_symbol, name='EXMO'):
        super().__init__(base_symbol, quote_symbol, name)
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

