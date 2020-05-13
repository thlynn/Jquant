import threading

from api.base_api import BaseAPI


class MonitorBase(threading.Thread):

    def __init__(self, orders, callback, trade_api: BaseAPI):
        super().__init__()
        self.orders = orders
        self.callback = callback

        self.trade_api = trade_api

    def run(self) -> None:
        while True:
            self.monitor_order()

    def monitor_order(self):
        for order in self.orders.values():
            if order:
                self.trade_api.get_contract_order_info(order)
                self.callback(order)
