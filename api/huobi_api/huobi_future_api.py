from api.base_api import BaseAPI
from api.huobi_api.HuobiDMService import HuobiDM
from model.BaseModel import OrderFuture


class HUOBIFutureAPI(BaseAPI):

    def __int__(self):
        super().__int__()
        self.huobi_dm = HuobiDM()

    def send_contract_order(self, callback):
        pass

    def get_contract_order_info(self, order: OrderFuture):
        response = self.huobi_dm.get_contract_order_info(order.base_symbol, '', order.order_client_id)
        if response['status'] == 'ok':
            data = response['data'][0]

            order_status = data['status']
            if order_status == 4:
                order.order_status = 'partially_matched'
            elif order_status == 5:
                order.order_status = 'cancelled_with_partially_matched'
            elif order_status == 6:
                order.order_status = 'fully_matched'
            elif order_status == 7:
                order.order_status = 'cancelled'
            elif order_status == 11:
                order.order_status = 'cancelling'

            order.trade_volume = data['trade_volume']
            order.trade_avg_price = data['trade_avg_price']
        else:
            err_msg = response['err_msg']
            # TODO: raise exception

