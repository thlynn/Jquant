from api.huobi_api.huobi_future_api import HUOBIFutureAPI
from model.BaseModel import OrderFuture
from monitor.monitor_base import MonitorBase
from typing import Sequence, Dict


class HUOBIOrderMonitor(MonitorBase):

    def __int__(self, orders: Dict[str: OrderFuture], callback):
        super().__int__()
        self.orders = orders
        self.callback = callback
        self.huobi_future_api = HUOBIFutureAPI()

    def run(self) -> None:
        while True:
            # TODO: get updates of all orders
            for order in self.orders.values():
                self.huobi_future_api.get_contract_order_info(order)
                self.callback(order)


