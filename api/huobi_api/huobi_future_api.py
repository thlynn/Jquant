import time
from decimal import Decimal

from api.base_api import BaseAPI
from api.huobi_api.HuobiDMService import HuobiDM
from core.logger import get_logger
from model.BaseModel import OrderFuture
from datetime import datetime


class HUOBIFutureAPI(BaseAPI):

    def __init__(self, access_key, secret_key, base_url, contract_type, contract_code):
        super().__init__()
        self.base_url = base_url
        self.huobi_dm = HuobiDM(base_url, access_key, secret_key)
        self.client_order_id = int(datetime.timestamp(datetime.now()))

        self.contract_type = contract_type
        self.contract_code = contract_code

        self.logger = get_logger('trade_api')

    def send_contract_order(self, order: OrderFuture):
        self.client_order_id += 1
        order.order_client_id = self.client_order_id

        self.logger.info(f'''Place Order:{order.order_client_id};
            price:{order.price};volume:{order.volume};order_type:{order.order_type};offset:{order.offset};direction:{order.direction}''')

        response = self.huobi_dm.send_contract_order(
            order.base_symbol, self.contract_type, self.contract_code,
            self.client_order_id, order.price, order.volume,
            order.direction, order.offset, order.lever_rate, order.order_type)
        if response['status'] == 'ok':
            return True
        else:
            err_code = response.get('err_code', 0)
            self.logger.warn(f"order_client_id:{order.order_client_id};err_code:{err_code};err_msg:{response['err_msg']}")
            # Insufficient close amount available
            if err_code == 1048:
                self.huobi_dm.cancel_all_contract_order(str.upper(order.base_symbol))
            return False

    def cancel_contract_order(self, order: OrderFuture):
        self.logger.info(f'Cancel Order:{order.order_client_id}')

        response = self.huobi_dm.cancel_contract_order(order.base_symbol, client_order_id=order.order_client_id)
        if response['status'] == 'ok':
            return True
        else:
            self.logger.warn(response['err_msg'])
            time.sleep(1)
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

            order.trade_volume = int(data['trade_volume'])
            trade_avg_price = data['trade_avg_price']
            if trade_avg_price and not isinstance(trade_avg_price, Decimal):
                order.trade_avg_price = Decimal(str(trade_avg_price))

            order.created = data['created_at']

            self.logger.info(f'''Order Status:{order.order_client_id};
                trade_volume:{order.trade_volume};trade_avg_price:{order.trade_avg_price};
                status:{order.order_status}''')

            return True
        else:
            err_code = response.get('err_code', 0)
            self.logger.warn(f"order_client_id:{order.order_client_id};err_code:{err_code};err_msg:{response['err_msg']}")
            if err_code == 1017:
                order.order_status = 'not_exit'
            return False

