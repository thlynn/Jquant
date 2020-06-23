from decimal import Decimal

from api.base_api import BaseAPI
from app.base_strategy import BaseStrategy
from data.tools import atr, donchian
from model.BaseModel import Bar, OrderFuture


class TurtleV1(BaseStrategy):

    def __init__(
            self, symbol, pos: int, entry_window: int, exit_window: int, atr_window: int,
            trade_api: BaseAPI, intervals):
        super().__init__(symbol, trade_api)
        self.pos = pos
        self.intervals = intervals

        # attributes
        self.entry_window = entry_window
        self.exit_window = exit_window
        self.atr_window = atr_window

        # parameters
        self.entry_up, self.entry_down = (Decimal('0'), Decimal('0'))
        self.exit_up, self.exit_down = (Decimal('0'), Decimal('0'))
        self.atr_value = Decimal(0)

        # variables
        self.long_pos_last_price = Decimal('0')
        self.long_pos = 0
        self.long_increased_times = 0
        self.short_pos_last_price = Decimal('0')
        self.short_pos = 0
        self.short_increased_times = 0

        self.long_pos_stop_loss_price = Decimal('0')
        self.short_pos_stop_loss_price = Decimal('0')

        self.orders_dict['open_buy'] = None
        self.orders_dict['open_sell'] = None
        self.orders_dict['close_buy'] = None
        self.orders_dict['close_sell'] = None

        self.last_bar_timestamp = 0

    def calculate_parameters(self):
        bars_dict = getattr(self, f'bars_{self.intervals}')
        tmp_atr_value = atr(self.atr_window, bars_dict)
        if tmp_atr_value:
            # self.atr_value = max(tmp_atr_value, Decimal(50))
            self.atr_value = tmp_atr_value
        else:
            self.logger.warn(f'atr_value calculated is None: {tmp_atr_value}')
            self.logger.debug(bars_dict)

        # entry
        tmp_entry_up, tmp_entry_down = donchian(self.entry_window, bars_dict)
        if not tmp_entry_up or not tmp_entry_down:
            self.logger.warn(f'tmp_entry_up or tmp_entry_down calculated is None, tmp_entry_up:{tmp_entry_up},tmp_entry_down:{tmp_entry_down}')
            self.logger.debug(bars_dict)
        if tmp_entry_up and tmp_entry_up != self.entry_up:
            self.entry_up = tmp_entry_up
        if tmp_entry_down and tmp_entry_down != self.entry_down:
            self.entry_down = tmp_entry_down
        # exit
        tmp_exit_up, tmp_exit_down = donchian(self.exit_window, bars_dict)
        if not tmp_exit_up or not tmp_exit_down:
            self.logger.warn(f'tmp_entry_up or tmp_entry_down calculated is None, tmp_exit_up:{tmp_exit_up},tmp_exit_down:{tmp_exit_down}')
            self.logger.debug(bars_dict)
        if tmp_exit_up and tmp_exit_up != self.exit_up:
            self.exit_up = tmp_exit_up
        if tmp_exit_down and tmp_exit_down != self.exit_down:
            self.exit_down = tmp_exit_down

        self.logger.debug(
            f'''timestamp:{bars_dict['timestamp'][-1]},
                entry_up:{self.entry_up},entry_down:{self.entry_down},
                atr_value:{self.atr_value}, df_len:{len(bars_dict['close'])}
                exit_up:{self.exit_up},exit_down:{self.exit_down}''')

    def on_bar(self, bar: Bar):
        self.update_bars(bar, self.intervals)

        bars_dict = getattr(self, f'bars_{self.intervals}')
        timestamp = bars_dict['timestamp'][-1]
        if self.last_bar_timestamp != timestamp:
            self.calculate_parameters()
            for order in self.orders_dict.values():
                if order and order.offset == 'open':
                    self.cancel_contract_order(order)
            self.last_bar_timestamp = timestamp

        order_open_buy = self.orders_dict.get('open_buy', None)
        order_open_sell = self.orders_dict.get('open_sell', None)

        if not order_open_sell:
            price = Decimal('0')
            if self.short_pos > 0 and self.short_increased_times < 4:
                price = self.short_pos_last_price - round(self.atr_value * Decimal('0.5'), 2)
            elif self.entry_down and self.short_pos == 0:
                price = self.entry_down - 20
            if price and bar.close_price <= price:
                order = OrderFuture(
                    self.symbol, 'sell', 'open', price, self.pos, 'limit')
                self.place_contract_order(order)

        if not order_open_buy:
            price = Decimal('0')
            if self.long_pos > 0 and self.long_increased_times < 4:
                price = self.long_pos_last_price + round(self.atr_value * Decimal('0.5'), 2)
            elif self.entry_up and self.long_pos == 0:
                price = self.entry_up + 20

            if price and bar.close_price >= price:
                order = OrderFuture(
                    self.symbol, 'buy', 'open', price, self.pos, 'limit')
                self.place_contract_order(order)

        order_close_buy = self.orders_dict.get('close_buy', None)
        order_close_sell = self.orders_dict.get('close_sell', None)

        if self.short_pos > 0 and not order_close_buy:
            price = Decimal('0')
            if self.short_pos_stop_loss_price and bar.close_price >= self.short_pos_stop_loss_price:
                # stop loss
                price = bar.close_price
            elif self.exit_up and bar.close_price > self.exit_up:
                # stop profit
                price = bar.close_price
            if price:
                order = OrderFuture(
                    self.symbol, 'buy', 'close', price, self.short_pos, 'opponent_ioc')
                self.place_contract_order(order)

        if self.long_pos > 0 and not order_close_sell:
            price = Decimal('0')
            if self.long_pos_stop_loss_price and bar.close_price <= self.long_pos_stop_loss_price:
                # stop loss
                price = bar.close_price
            elif self.exit_down and bar.close_price < self.exit_down:
                # stop profit
                price = bar.close_price
            if price:
                order = OrderFuture(
                    self.symbol, 'sell', 'close', price, self.long_pos, 'opponent_ioc')
                self.place_contract_order(order)

    def place_contract_order(self, order: OrderFuture):
        key = f'{order.offset}_{order.direction}'
        self.orders_dict[key] = order

        order.price = round(order.price, 2)
        self.trade_api.send_contract_order(order)

    def cancel_contract_order(self, order: OrderFuture):
        self.trade_api.cancel_contract_order(order)

    def on_trade(self, order: OrderFuture):
        key = f'{order.offset}_{order.direction}'
        if order.order_status in ['cancelled_with_partially_matched', 'fully_matched']:
            if order.offset == 'open' and order.direction == 'buy':
                self.long_pos_last_price = order.trade_avg_price
                # self.long_pos_last_price = order.price
                self.long_pos += order.trade_volume
                self.long_pos_stop_loss_price = self.long_pos_last_price - round(2 * self.atr_value, 2)
                self.long_increased_times += 1
            elif order.offset == 'open' and order.direction == 'sell':
                self.short_pos_last_price = order.trade_avg_price
                # self.short_pos_last_price = order.price
                self.short_pos += order.trade_volume
                self.short_pos_stop_loss_price = self.short_pos_last_price + round(2 * self.atr_value, 2)
                self.short_increased_times += 1
            elif order.offset == 'close' and order.direction == 'buy':
                self.short_pos -= order.trade_volume
            elif order.offset == 'close' and order.direction == 'sell':
                self.long_pos -= order.trade_volume

            if self.long_pos == 0:
                self.long_pos_last_price = Decimal('0')
                self.long_pos_stop_loss_price = Decimal('0')
                self.long_increased_times = 0

            if self.short_pos == 0:
                self.short_pos_last_price = Decimal('0')
                self.short_pos_stop_loss_price = Decimal('0')
                self.short_increased_times = 0

            self.orders_dict[key] = None
        elif order.order_status == 'partially_matched':
            self.cancel_contract_order(order)
        elif order.order_status == 'cancelled':
            self.orders_dict[key] = None
        elif order.order_status == 'not_exit':
            self.orders_dict[key] = None
