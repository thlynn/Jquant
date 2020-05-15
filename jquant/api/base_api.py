from jquant.model.BaseModel import OrderFuture


class BaseAPI:

    def __init__(self):
        pass

    def send_contract_order(self, order: OrderFuture) -> bool:
        pass

    def cancel_contract_order(self, order: OrderFuture) -> bool:
        pass

    def get_contract_order_info(self, order: OrderFuture):
        pass
