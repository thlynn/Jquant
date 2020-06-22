from decimal import Decimal

from typing import Sequence, Dict

import numpy as np

from core.exceptions import TimestampError
from core.logger import get_logger
from model.BaseModel import Bar


class BaseStrategy:

    def __init__(self, trade_api, array_size=2000):
        self.array_size = array_size

        self.bars_1min = {
            'timestamp': np.zeros(self.array_size), 'open': np.zeros(self.array_size), 'high': np.zeros(self.array_size),
            'low': np.zeros(self.array_size), 'close': np.zeros(self.array_size), 'amount': np.zeros(self.array_size)}

        self.bars_5min = {
            'timestamp': np.zeros(self.array_size), 'open': np.zeros(self.array_size), 'high': np.zeros(self.array_size),
            'low': np.zeros(self.array_size), 'close': np.zeros(self.array_size), 'amount': np.zeros(self.array_size)}

        self.bars_15min = {
            'timestamp': np.zeros(self.array_size), 'open': np.zeros(self.array_size), 'high': np.zeros(self.array_size),
            'low': np.zeros(self.array_size), 'close': np.zeros(self.array_size), 'amount': np.zeros(self.array_size)}

        self.bars_30min = {
            'timestamp': np.zeros(self.array_size), 'open': np.zeros(self.array_size), 'high': np.zeros(self.array_size),
            'low': np.zeros(self.array_size), 'close': np.zeros(self.array_size), 'amount': np.zeros(self.array_size)}

        self.bars_60min = {
            'timestamp': np.zeros(self.array_size), 'open': np.zeros(self.array_size), 'high': np.zeros(self.array_size),
            'low': np.zeros(self.array_size), 'close': np.zeros(self.array_size), 'amount': np.zeros(self.array_size)}

        self.orders: Sequence[object] = list()
        self.orders_dict: Dict[str: object] = dict()

        self.trade_api = trade_api

        # logger
        self.logger = get_logger('strategy')

    def init_bars(self, bars, intervals):
        for bar in bars:
            self.update_bars(bar, intervals)

        self.calculate_parameters()

        self.logger.info('history data initialized')

    def update_minute_bars(self, bars, bar, minutes):
        timestamp = bar.timestamp - (bar.timestamp % (minutes*60))

        if len(bars['close']) == 0 or timestamp > bars['timestamp'][-1]:
            bars['timestamp'][:-1] = bars['timestamp'][1:]
            bars['timestamp'][-1] = timestamp

            bars['open'][:-1] = bars['open'][1:]
            bars['open'][-1] = bar.open_price

            bars['high'][:-1] = bars['high'][1:]
            bars['high'][-1] = bar.high_price

            bars['low'][:-1] = bars['low'][1:]
            bars['low'][-1] = bar.low_price

            bars['close'][:-1] = bars['close'][1:]
            bars['close'][-1] = bar.close_price

            bars['amount'][:-1] = bars['amount'][1:]
            bars['amount'][-1] = bar.amount
        elif len(bars['close']) > 0 and timestamp == bars['timestamp'][-1]:
            bars['close'][-1] = bar.close_price
            if bars['high'][-1] < bar.high_price:
                bars['high'][-1] = bar.high_price
            if bars['low'][-1] > bar.low_price:
                bars['low'][-1] = bar.low_price
            bars['amount'][-1] = Decimal(str(bars['amount'][-1])) + Decimal(str(bar.amount))
        else:
            self.logger.error(f"last_bar_timestamp:{bars['timestamp'][-1]}, bar_timestamp:{bar.timestamp}")
            raise TimestampError()

    def calculate_parameters(self):
        pass

    def update_bars(self, bar: Bar, intervals):
        minutes = 0
        if intervals == '1min':
            minutes = 1
        elif intervals == '5min':
            minutes = 5
        elif intervals == '15min':
            minutes = 15
        elif intervals == '60min':
            minutes = 60
        if minutes:
            bar_dict = getattr(self, f'bars_{intervals}')
            self.update_minute_bars(bar_dict, bar, minutes)

    def place_contract_order(self, order: object):
        pass

    def cancel_contract_order(self, order: object):
        pass

    def on_bar(self, bar: Bar):
        pass

    def on_trade(self, response):
        pass
