import time
import traceback

from api.base_api import BaseAPI
from monitor.monitor_base import MonitorBase


class HUOBIOrderMonitor(MonitorBase):

    def __init__(self, orders, callback, trade_api: BaseAPI):
        super().__init__()
        self.orders = orders
        self.callback = callback

        self.trade_api = trade_api

    def run(self) -> None:
        while True:
            for order in self.orders.values():
                self.trade_api.get_contract_order_info(order)
                self.logger.debug(f'{order.price},{order.offset},{order.direction}{order.volume},{order.order_status}')
                self.callback(order)
                time.sleep(1)


