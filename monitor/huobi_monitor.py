import time
import traceback

from api.huobi_api.huobi_future_api import HUOBIFutureAPI
from monitor.monitor_base import MonitorBase


class HUOBIOrderMonitor(MonitorBase):

    def __init__(self, orders, callback):
        super().__init__()
        self.orders = orders
        self.callback = callback
        self.huobi_future_api = HUOBIFutureAPI()

    def run(self) -> None:
        while True:
            for order in self.orders.values():
                try:
                    self.huobi_future_api.get_contract_order_info(order)
                except Exception:
                    traceback.print_exc()
                    continue
                self.callback(order)
                time.sleep(1)


