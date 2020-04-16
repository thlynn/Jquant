import datetime

import pandas as pd

from model.BaseModel import Bar


class BaseStrategy:

    def __init__(self, base_symbol, quote_symbol):
        self.base_symbol = base_symbol
        self.quote_symbol = quote_symbol
        self.df_minute_bars: pd.DataFrame = None

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
        elif bar_timestamp == last_bar.name:
            last_bar['close_price'] = bar.close_price
            if last_bar['high_price'] < bar.high_price:
                last_bar['high_price'] = bar.high_price
            if last_bar['low_price'] > bar.low_price:
                last_bar['low_price'] = bar.low_price
        else:
            # TODO: raise exception
            pass

    def on_bar(self, bar: Bar):
        pass

    def on_trade(self):
        pass

