import datetime
from typing import Sequence, Dict

import pandas as pd

from core.exceptions import TimestampError
from model.BaseModel import Bar, OrderFuture


class BaseStrategy:

    def __init__(self, base_symbol, quote_symbol, lever_rate=1):
        self.base_symbol = base_symbol
        self.quote_symbol = quote_symbol
        self.lever_rate = lever_rate
        self.df_minute_bars: pd.DataFrame = None
        self.orders: Sequence[OrderFuture] = list()
        self.orders_dict: Dict[str: OrderFuture] = dict()

    def init_bars(self, bars):
        self.df_minute_bars = pd.DataFrame(data=[bar.__dict__ for bar in bars])
        self.df_minute_bars.drop_duplicates(inplace=True)
        self.df_minute_bars.set_index('timestamp', inplace=True)
        self.df_minute_bars.sort_index(inplace=True)

    def calculate_parameters(self):
        pass

    def update_bars(self, bar: Bar):
        bar_timestamp = Bar.timestamp
        bar_datetime = datetime.datetime.fromtimestamp(bar_timestamp)
        bar_timestamp -= bar_datetime.second
        
        last_bar = self.df_minute_bars.iloc[-1]

        if bar_timestamp > last_bar.name:
            self.df_minute_bars.append(pd.DataFrame([bar.__dict__]).set_index('timestamp'))
            return 'add'
        elif bar_timestamp == last_bar.name:
            last_bar['close_price'] = bar.close_price
            if last_bar['high_price'] < bar.high_price:
                last_bar['high_price'] = bar.high_price
            if last_bar['low_price'] > bar.low_price:
                last_bar['low_price'] = bar.low_price
            return 'update'
        else:
            raise TimestampError()

    def place_contract_order(self, order: OrderFuture):
        pass

    def cancel_contract_order(self, order: OrderFuture):
        pass

    def on_bar(self, bar: Bar):
        pass

    def on_trade(self, response):
        pass
