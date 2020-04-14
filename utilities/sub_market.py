import threading
import gzip
import json
import time
from decimal import Decimal

import requests
from websocket import create_connection
from utilities.tools import inflate
from datetime import datetime


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

    def __init__(self, name):
        super().__init__(name=name)
        self.timestamp = None
        self.close = None


class SubscribeHUOBI(Subscribe):

    def __init__(self, base_symbol, quote_symbol, name='HUOBI'):
        super().__init__(name=name)
        self.ws_url = create_connection("wss://api.huobi.pro/ws")
        topic = {
            "sub": f"market.{str.lower(base_symbol)}{str.lower(quote_symbol)}.kline.1min",
            "id": "id1"
        }
        self.ws_url.send(json.dumps(topic))

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
                self.timestamp = tick['id']
                self.close = Decimal(str(tick['close']))


class SubscribeEXMO(Subscribe):

    def __init__(self, base_symbol, quote_symbol, name='EXMO'):
        super().__init__(name=name)
        self.ticker_url = "https://api.exmo.com/v1/ticker/"
        self.base_symbol = base_symbol
        self.quote_symbol = quote_symbol

    def run(self):
        while True:
            time.sleep(0.5)
            try:
                res = requests.get(self.ticker_url, timeout=5)
            except requests.exceptions.ProxyError or requests.exceptions.SSLError or requests.exceptions.ReadTimeout:
                continue
            ticker = json.loads(res.content)[f'{str.upper(self.base_symbol)}_{str.upper(self.quote_symbol)}']
            updated = ticker['updated']

            self.timestamp = updated
            self.close = Decimal(str(ticker['last_trade']))

