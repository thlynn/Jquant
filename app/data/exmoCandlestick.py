import datetime
import json
import time
from decimal import Decimal

import requests
from pytz import timezone

from app.data.baseCandlestick import BaseCandlestick
from model.BaseModel import Bar


class EXMOCandlestick(BaseCandlestick):

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

