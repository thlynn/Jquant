from decimal import Decimal

from app.data.baseCandlestick import BaseCandlestick
from model.BaseModel import Bar, Exchange


class HuobiCandlestick(BaseCandlestick):

    url = "wss://www.hbdm.com/ws"

    def __init__(self, base_symbol, quote_symbol, intervals='1min'):
        super().__init__(base_symbol, quote_symbol, intervals)
        base_url = 'https://api.huobi.pro/market/history/kline'
        self.req_str = f'{base_url}?period={self.intervals}&size=2000&symbol={self.base_symbol}{self.quote_symbol}'

    def parse_data(self, data):
        for item in data:
            symbol = f'{self.base_symbol}_{self.quote_symbol}'
            bar = Bar(
                symbol, 'huobi', self.intervals, item['id'],
                Decimal(str(item['open'])), Decimal(str(item['high'])),
                Decimal(str(item['low'])), Decimal(str(item['close'])), Decimal(str(item['amount'])))
            self.bars.append(bar)

