import dataclasses
import json
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class Exchange(Enum):
    HUOBI = 'huobi'
    OKEX = 'okex'


@dataclass
class OrderFuture:
    symbol: str
    # sell/buy
    direction: str
    # open/close
    offset: str
    price: Decimal
    volume: int
    # limit/market order
    order_type: str
    order_client_id: int = 0
    trade_volume: Decimal = Decimal('0')
    trade_avg_price: Decimal = Decimal('0')
    # pending  completed
    order_status: str = 'pending'
    created: int = 0


@dataclass()
class TradeInfo:

    # 委托数量
    volume: Decimal
    # 交易方向 buy sell
    direction: str
    # open close
    offset: str
    # 成交量
    trade_volume: Decimal
    # 成交均价
    price_avg: Decimal


@dataclass
class Bar:
    symbol: str
    exchange: str
    period: str
    timestamp: int
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    # Accumulated trading volume, in base currency
    amount: Decimal = Decimal('0')
    # Accumulated trading value, in quote currency
    volume: Decimal = Decimal('0')
    open_interest: Decimal = Decimal('0')


@dataclass()
class Tick:

    timestamp: int
    # Accumulated trading volume, in base currency
    volume: Decimal
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)
