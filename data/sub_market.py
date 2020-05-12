import threading
import json
import time
from decimal import Decimal

import requests
from websocket import create_connection
from datetime import datetime

from core.logger import get_logger
from data.tools import inflate


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
