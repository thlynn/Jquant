from model.BaseModel import OrderFuture


class BaseAPI:

    def __init__(self, access_key, secret_key, base_url):
        self.client_order_id = 0
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = base_url

    def send_contract_order(self, order: OrderFuture, contract_type, contract_code) -> bool:
        pass

    def cancel_contract_order(self, order: OrderFuture) -> bool:
        pass

    def get_contract_order_info(self, order: OrderFuture):
        pass
