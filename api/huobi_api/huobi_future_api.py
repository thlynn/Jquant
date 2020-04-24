from api.base_api import BaseAPI
from api.huobi_api.HuobiDMService import HuobiDM
from core.exceptions import APIError
from core.logger import get_logger
from model.BaseModel import OrderFuture
from datetime import datetime


class HUOBIFutureAPI(BaseAPI):

    def __init__(self, access_key, secret_key, base_url):
        super().__init__(access_key, secret_key, base_url)
        self.huobi_dm = HuobiDM(base_url, access_key, secret_key)
        self.client_order_id = int(datetime.timestamp(datetime.now()))
        self.logger = get_logger('trade_api')

    def send_contract_order(self, order: OrderFuture, contract_type, contract_code):
        self.client_order_id += 1
        order.order_client_id = self.client_order_id
        response = self.huobi_dm.send_contract_order(
            order.base_symbol, contract_type, contract_code,
            self.client_order_id, order.price, order.volume,
            order.direction, order.offset, order.lever_rate, order.order_type)
        if response['status'] == 'ok':
            return True
        else:
            self.logger.warn(response['err_msg'])
            return False

    def cancel_contract_order(self, order: OrderFuture):
        response = self.huobi_dm.cancel_contract_order(order.base_symbol, client_order_id=order.order_client_id)
        if response['status'] == 'ok':
            return True
        else:
            self.logger.warn(response['err_msg'])
            return False

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
            raise APIError(err_msg)

