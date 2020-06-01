from datetime import datetime
from decimal import Decimal

import pytz

from api.base_api import BaseAPI
from core.logger import get_logger
from data.tools import calculate_pos_and_average_price
from model.BaseModel import OrderFuture, Bar


class BackTestAPI(BaseAPI):

    def __init__(self):
        super().__init__()
        self.logger = get_logger('test_back_api')
        self.orders = list()
        self.uncompleted_orders = dict()
        self.completed_orders = dict()
        self.long_pos = {'volume': 0, 'price': Decimal('0')}
        self.short_pos = {'volume': 0, 'price': Decimal('0')}
        self.fee_rate = Decimal('0.0003')
        self.client_order_id = int(datetime.timestamp(datetime.now()))

    def send_contract_order(self, order: OrderFuture):
        self.client_order_id += 1
        order.order_client_id = self.client_order_id

        order.created = datetime.now(tz=pytz.timezone('Asia/Shanghai'))

        if order.order_type == 'limit':
            self.send_limit_order(order)
        else:
            self.complete_order(order)

    def send_limit_order(self, order: OrderFuture):
        self.logger.info(f'''Place Limit Order:
            price:{order.price};volume:{order.volume};order_type:{order.order_type};offset:{order.offset};direction:{order.direction}''')
        self.uncompleted_orders[order.order_client_id] = order

    def complete_order(self, order: OrderFuture):
        offset = order.offset
        direction = order.direction
        price = order.price
        volume = order.volume

        # slippage
        # if direction == 'buy':
        #     price += Decimal(10)
        # elif direction == 'sell':
        #     price -= Decimal(10)

        order.trade_volume = order.volume
        order.trade_avg_price = price

        self.logger.info(f'''Complete Order:
            price:{price};volume:{volume};order_type:{order.order_type};offset:{offset};direction:{direction}''')

        fee = Decimal(100) * Decimal(volume) * self.fee_rate / price
        profit = Decimal('0')

        if offset == 'open' and direction == 'buy':
            self.long_pos['volume'], self.long_pos['price'] = \
                calculate_pos_and_average_price(self.long_pos['volume'], self.long_pos['price'], volume, price)
        elif offset == 'open' and direction == 'sell':
            self.short_pos['volume'], self.short_pos['price'] = \
                calculate_pos_and_average_price(self.short_pos['volume'], self.short_pos['price'], volume, price)
        elif offset == 'close' and direction == 'sell':
            self.long_pos['volume'] -= volume
            profit = (price - self.long_pos['price']) / self.long_pos['price'] * Decimal(volume) * Decimal(100) / price
        elif offset == 'close' and direction == 'buy':
            self.short_pos['volume'] -= volume
            profit = (self.short_pos['price'] - price) / self.short_pos['price'] * Decimal(volume) * Decimal(100) / price

        order.order_status = 'fully_matched'

        order_info = order.__dict__
        order_info['fee'] = fee
        order_info['profit'] = profit
        order_info['account'] = profit - fee

        self.orders.append(order_info)
        self.uncompleted_orders.pop(order.order_client_id, None)

        self.completed_orders[order.order_client_id] = order

        return True

    def cancel_contract_order(self, order: OrderFuture):
        order = self.uncompleted_orders.pop(order.order_client_id, None)
        if order:
            order.order_status = 'cancelled'
        return True

    def get_contract_order_info(self, order: OrderFuture):
        stored_order = self.completed_orders.get(order.order_client_id, None)
        if stored_order and stored_order.order_status == 'fully_matched':
            order.order_status = 'fully_matched'
        return True

    def on_bar(self, bar: Bar):
        for order in self.uncompleted_orders.values():
            if order.direction == 'buy' and bar.close_price <= order.price:
                self.complete_order(order)
                break
            elif order.direction == 'sell' and bar.close_price >= order.price:
                self.complete_order(order)
                break
