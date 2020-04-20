from model.BaseModel import OrderFuture


class BaseAPI:

    def __int__(self):
        self.client_order_id = 0

    def send_contract_order(self, order: OrderFuture, contract_type, contract_code):
        pass

    def get_contract_order_info(self, order: OrderFuture):
        pass
