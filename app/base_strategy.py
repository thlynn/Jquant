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
        self.df_minute_bars: pd.DataFrame = None
        self.orders: Sequence[object] = list()
        self.orders_dict: Dict[str: object] = dict()

        self.trade_api = trade_api

        # logger
        self.logger = get_logger('strategy')

    def init_bars(self, bars):
        self.df_minute_bars = pd.DataFrame(data=bars)
        self.df_minute_bars.drop_duplicates(inplace=True)
        self.df_minute_bars.set_index('timestamp', inplace=True)
        self.df_minute_bars.sort_index(inplace=True)

        self.calculate_parameters()

        self.logger.info('history data initialized')

    def calculate_parameters(self):
        pass

    def update_bars(self, bar: Bar):
        bar_timestamp = bar.timestamp
        bar_datetime = datetime.datetime.fromtimestamp(bar_timestamp)
        bar_timestamp -= bar_datetime.second

        last_bar = self.df_minute_bars.iloc[-1]
        last_bar_timestamp = int(datetime.datetime.timestamp(last_bar.name))

        if bar_timestamp > last_bar_timestamp:
            bar.timestamp = datetime.datetime.fromtimestamp(bar_timestamp, tz=pytz.utc)
            self.df_minute_bars = self.df_minute_bars.append(pd.DataFrame([bar.__dict__]).set_index('timestamp')).iloc[1:]
            return 'add'
        elif bar_timestamp == last_bar_timestamp:
            last_bar['close_price'] = bar.close_price
            if last_bar['high_price'] < bar.high_price:
                last_bar['high_price'] = bar.high_price
            if last_bar['low_price'] > bar.low_price:
                last_bar['low_price'] = bar.low_price
            return 'update'
        else:
            self.logger.error(f'last_bar_timestamp:{last_bar_timestamp},bar_timestamp:{bar_timestamp}')
            raise TimestampError()

    def place_contract_order(self, order: object):
        pass

    def cancel_contract_order(self, order: object):
        pass

    def on_bar(self, bar: Bar):
        pass

    def on_trade(self, response):
        pass
