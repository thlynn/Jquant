import datetime
import json
import time
from decimal import Decimal

import requests
from pytz import timezone

from data.candlesticks import BaseCandlestick
from data.subscribe import Subscribe
from model.BaseModel import Bar


class EXMOCandlestick(BaseCandlestick):

    def get_bars(self, numbers, begin=None, end=None):
        pass

    def get_close(self, numbers, begin=None, end=None):
        pass

    def __init__(self, base_symbol, quote_symbol, intervals='1min', numbers=0):
        super().__init__(base_symbol, quote_symbol, intervals)
        self.req_str = 'https://api.exmo.com/v1/ticker/'
        self.numbers = numbers

    def req_data(self):
        num = 0
        data = list()
        zone = timezone('UTC')
        minute = 0
        bar = None
        while num < self.numbers:
            time.sleep(0.5)
            try:
                if len(data) > 0:
                    bar = data[-1]
                res = requests.get(self.req_str)
                ticker = json.loads(res.content)[f'{self.base_symbol}_{self.quote_symbol}']
                updated = ticker['updated']
                ticker_date = datetime.datetime.fromtimestamp(updated, tz=zone)
                print(ticker)
                if not bar or minute != ticker_date.minute:
                    bar_timestamp = updated - ticker_date.second
                    bar = Bar(
                        f'{self.base_symbol}_{self.quote_symbol}', 'exmo', self.intervals, bar_timestamp,
                        Decimal(str(ticker['last_trade'])), Decimal(str(ticker['high'])),
                        Decimal(str(ticker['low'])), Decimal(str(ticker['last_trade'])))
                    minute = ticker_date.minute
                    data.append(bar)
                    num += 1
                    if num > 1:
                        print(data[-2])
                else:
                    bar.close_price = Decimal(str(ticker['last_trade']))
                    if bar.high_price < Decimal(str(ticker['high'])):
                        bar.high_price = Decimal(str(ticker['high']))
                    if bar.low_price > Decimal(str(ticker['low'])):
                        bar.low_price = Decimal(str(ticker['low']))
            except:
                continue
        return data

    def parse_data(self, data):
        self.bars = data


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
