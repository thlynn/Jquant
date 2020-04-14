from datetime import datetime
import time
import threading
from Jquant.config import Keys
from Jquant.api.huobi.HuobiDMService import HuobiDM
from Jquant.model.BaseModel import TradeInfo


class Tracker(threading.Thread):
    def __init__(self, dm, orderId, callback):
        super().__init__()
        self.orderId = orderId
        self.dm = dm
        self.callback = callback
        self.tradeInfo = TradeInfo()

    def run(self):
        time.sleep(30)
        while True:
            r = self.parse()
            if r['code'] == 1:
                if r['status'] != 7:
                    self.callback(self.tradeInfo)
                break

    def parse(self):
        # code 0.失败 1.成功 2.部分成功 -1.撤单失败
        # status, ok|error
        # 假设以对手价下单,未成交即撤单
        result = dict()
        result['code'] = -1
        result_info = self.dm.get_contract_order_info(
            "BTC", order_id=self.orderId)
        if 'data' not in result_info.keys():
            print('huobi,订单信息查询失败，status:{},orderId:{}'.format(
                  result_info.get('status'), self.orderId))
            result['code'] = -1
            return result
        info = result_info['data'][0]
        # 委托数量
        self.tradeInfo.volume = info['volume']
        # "buy":买 "sell":卖
        self.tradeInfo.direction = info['direction']
        # "open":开 "close":平
        self.tradeInfo.offset = info['offset']
        # 成交数量
        self.tradeInfo.trade_volume = info['trade_volume']
        # 成交均价
        self.tradeInfo.price_avg = info['trade_avg_price']
        # (1准备提交 2准备提交 3已提交 4部分成交 5部分成交已撤单 6全部成交 7已撤单 11撤单中)
        status = info['status']
        result['status'] = status
        # print(datetime.utcnow(), "huobi订单返回status:{}".format(status))
        if status == 6:
            print(datetime.utcnow(),
                  "huobi,全部成交,订单ID:{},成交均价:{}".format(
                  self.orderId, self.tradeInfo.price_avg))
            result['code'] = 1
        elif status == 1 or status == 2:
            pass
            # print(datetime.utcnow(),"huobi,准备提交,订单ID:{}".format(self.orderId))
        elif status == 3:
            pass
            # print(datetime.utcnow(),"huobi,已提交,订单ID:{}".format(self.orderId))
        elif status == 4:
            print(datetime.utcnow(), "huobi,部分成交,订单ID:{}".format(self.orderId))
        elif status == 5:
            volume_remain = self.tradeInfo.volume - self.tradeInfo.trade_volume
            print(datetime.utcnow(), "huobi,部分成交已撤单,剩余{}张,订单ID:{}".format(
                volume_remain, self.orderId))
            result['code'] = 1
        elif status == 7:
            print(datetime.utcnow(), "huobi,已撤单,订单ID:{}".format(self.orderId))
            result['code'] = 1
        elif status == 11:
            pass
            # print(datetime.utcnow(),"huobi,撤单中,订单ID:{}".format(self.orderId))

        return result


class Trader():

    symbol = 'btc'

    def __init__(self, leverage, callback, contract_type):
        super().__init__()
        self.VOLUME_TMP = 0
        self.LEVERAGE = leverage
        self.dm = HuobiDM(Keys.URL, Keys.ACCESS_KEY, Keys.SECRET_KEY)
        self.callback = callback
        self.contract_type = contract_type
        self.orderId = None

    def init_pos(self):
        pos = 0
        result_pos = self.dm.get_contract_position_info("BTC")
        if result_pos['status'] == "ok":
            for hold in result_pos['data']:
                if hold['contract_type'] == self.contract_type:
                    if hold['available'] != 0:
                        if hold['direction'] == "buy":
                            pos = int(hold['available'])
                        elif hold['direction'] == "sell":
                            pos = int(hold['available'])(-1)
        return pos

    def cancel_all(self):
        result = self.dm.cancel_all_contract_order('BTC')
        if result['status'] == 'error':
            print(result)

    def cancel_order(self):
        result_order_cancel = \
            self.dm.cancel_contract_order('BTC', order_id=self.orderId)
        if (result_order_cancel['status'] == 'ok'
                and result_order_cancel['data'].get('successes')
                and self.orderId ==
                int(result_order_cancel['data']['successes'])):
            print(datetime.utcnow(),
                  "huobi,撤单成功,订单ID:{}".format(self.orderId))
        else:
            for error in result_order_cancel['data']['errors']:
                if error['order_id'] == self.orderId:
                    print(
                        datetime.utcnow(),
                        "huobi,撤单失败,订单ID:{},err_code:{},err_msg:{}".
                        format(self.orderId, error['err_code'],
                               error['error']))

    def transaction(
            self, volume, direction, offset, price=None, orderType='opponent'):
        if price:
            price = round(price, 2)
        result = self.dm.send_contract_order(
            symbol=self.symbol, contract_type=self.contract_type,
            contract_code='', client_order_id='',
            price=price, volume=volume,
            direction=direction, offset=offset,
            lever_rate=self.LEVERAGE, order_price_type=orderType)
        if result['status'] == 'error':
            print('err_code:{}, err_msg:{}'.
                  format(result['err_code'], result['err_msg']))
        else:
            self.orderId = result['data']['order_id']
            tracker = Tracker(self.dm, self.orderId, self.callback)
            tracker.start()
