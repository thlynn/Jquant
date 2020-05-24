import datetime
from typing import Sequence, Dict

import pandas as pd
import pytz

from core.exceptions import TimestampError
from core.logger import get_logger
from model.BaseModel import Bar


class BaseStrategy:

    def __init__(self, base_symbol, quote_symbol, trade_api, lever_rate=1):
        self.base_symbol = base_symbol
        self.quote_symbol = quote_symbol
        self.lever_rate = lever_rate

        self.bars_1minutes = {
            'timestamp': list(), 'open': list(), 'high': list(),
            'low': list(), 'close': list(), 'amount': list()}

        self.bars_15minutes = {
            'timestamp': list(), 'open': list(), 'high': list(),
            'low': list(), 'close': list(), 'amount': list()}

        self.orders: Sequence[object] = list()
        self.orders_dict: Dict[str: object] = dict()

        self.trade_api = trade_api

        # logger
        self.logger = get_logger('strategy')

    def init_bars(self, bars):
        for bar in bars:
            self.bars_1minutes['timestamp'].append(bar.timestamp)
            self.bars_1minutes['open'].append(bar.open_price)
            self.bars_1minutes['high'].append(bar.high_price)
            self.bars_1minutes['low'].append(bar.low_price)
            self.bars_1minutes['close'].append(bar.close_price)
            self.bars_1minutes['amount'].append(bar.amount)
            self.update_minute_bars(self.bars_15minutes, bar, 15)

        self.calculate_parameters()

        self.logger.info('history data initialized')

    def update_minute_bars(self, bars, bar, minutes):
        timestamp = bar.timestamp - (bar.timestamp % minutes*60)

        if len(bars['close']) == 0 or timestamp > bars['timestamp'][-1]:
            bars['timestamp'].append(bar.timestamp)
            bars['open'].append(bar.open_price)
            bars['high'].append(bar.high_price)
            bars['low'].append(bar.low_price)
            bars['close'].append(bar.close_price)
            bars['amount'].append(bar.amount)

            if len(bars['close']) > 2000:
                bars['timestamp'] = bars['timestamp'][1:]
                bars['open'] = bars['open'][1:]
                bars['high'] = bars['high'][1:]
                bars['low'] = bars['low'][1:]
                bars['close'] = bars['close'][1:]
                bars['amount'] = bars['amount'][1:]
        elif len(bars['close']) > 0 and timestamp == bars['timestamp'][-1]:
            bars['close'][-1] = bar.close_price
            if bars['high'][-1] < bar.high_price:
                bars['high'][-1] = bar.high_price
            if bars['low'][-1] > bar.low_price:
                bars['low'][-1] = bar.low_price
            bars['amount'][-1] += bar.amount
        else:
            self.logger.error(f"last_bar_timestamp:{bars['timestamp'][-1]}, bar_timestamp:{bar.timestamp}")
            raise TimestampError()

    def calculate_parameters(self):
        pass

    def update_bars(self, bar: Bar):
        self.update_minute_bars(self.bars_1minutes, bar, 1)
        self.update_minute_bars(self.bars_15minutes, bar, 15)

    def place_contract_order(self, order: object):
        pass

    def cancel_contract_order(self, order: object):
        pass

    def on_bar(self, bar: Bar):
        pass

    def on_trade(self, response):
        pass
