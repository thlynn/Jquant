from api.okex.exceptions import OkexAPIException
import threading
from datetime import datetime
import time


class Trade(threading.Thread):

    symbol_okex = 'BTC-USD-190927'
    symbol_huobi = 'btc'

    VOLUME = 10

    def __init__(self, pos, queue, dm, futureAPI, leverage):
        super().__init__()
        self.pos = pos
        self.queue = queue
        self.dm = dm
        self.futureAPI = futureAPI
        self.VOLUME_TMP = 0
        self.LEVERAGE = leverage

    def run(self):
        while True:
            # mp 1.以对手价下单  f:buy t:huobi
            f, t, p, mp = self.queue.get()
            self.pos['flag_{}'.format(t)] = 0
            self.VOLUME_TMP = 0
            fun = getattr(self, "{}_{}".format(f, t))
            r = dict()
            r['code'] = 0
            while True:
                if r['code'] == 1:
                    self.pos['flag_{}'.format(t)] = 1
                    break
                try:
                    r = fun(p, mp)
                    print("当前持仓,huobi:{},okex:{}".format(self.pos['pos_huobi'],
                          self.pos['pos_okex']))
                    # if r['code'] == 2:
                    #     for i in range(r['remain']):
                    #         self.queue.put((f, t, p, mp))
                except OkexAPIException as e:
                    # 32019 Order price cannot be more than 103%
                    #  or less than 97% of the previous minute price
                    # 32014 您的平仓张数大于该仓位的可平张数
                    # 30003 OK-ACCESS-TIMESTAMP header is required
                    print(e.code, e.message)
                    if e.code == 32019 or e.code == 32014:
                        time.sleep(0.5)
                        self.init_pos_okex()
                        r['code'] = 0
                    elif e.code == 30003:
                        r['code'] = 1

    def init_pos_okex(self):
        self.pos['pos_okex'] = 0
        result_pos = self.futureAPI.get_position()
        if result_pos['result']:
            for hold in result_pos['holding'][0]:
                if hold['instrument_id'] == self.symbol_okex:
                    if hold['long_avail_qty'] != '0':
                        self.pos['pos_okex'] = int(hold['long_avail_qty'])
                    elif hold['short_avail_qty'] != '0':
                        self.pos['pos_okex'] = \
                            int(hold['short_avail_qty'])*(-1)
        print("初始头寸,okex:{},flag_okex:{}".format(
              self.pos['pos_okex'], self.pos['flag_okex']))

    def init_pos_huobi(self):
        self.pos['pos_huobi'] = 0
        result_pos_huobi = self.dm.get_contract_position_info("BTC")
        if result_pos_huobi['status'] == "ok":
            for hold in result_pos_huobi['data']:
                if hold['contract_type'] == "quarter":
                    if hold['available'] != 0:
                        if hold['direction'] == "buy":
                            self.pos['pos_huobi'] = int(hold['available'])
                        elif hold['direction'] == "sell":
                            self.pos['pos_huobi'] = int(hold['available'])*(-1)
        print("初始头寸,huobi:{},flag_huobi:{}".format(
              self.pos['pos_huobi'], self.pos['flag_huobi']))

    def init_pos(self):
        self.init_pos_okex()
        self.init_pos_huobi()

    def parse_okex(self, result_origin):
        time.sleep(0.5)
        # code 0.失败 1.成功 2.部分成功 -1.撤单失败
        result = dict()
        orderId = result_origin['order_id']
        result_order_info = self.futureAPI.get_order_info(
            self.symbol_okex, order_id=orderId)
        state_info = result_order_info['state']
        # 委托数量
        size = int(result_order_info['size'])
        # 成交数量
        filledQty = int(result_order_info['filled_qty'])
        # 成交均价
        priceAvg = result_order_info['price_avg']
        # 订单类型(1:开多 2:开空 3:平多 4:平空)
        otype = result_order_info['type']
        # 订单状态("-2":失败,"-1":撤单成功,"0":等待成交 ,"1":部分成交, "2":完全成交,"3":下单中,"4":撤单中,）
        if state_info == "2":
            result['code'] = 1
            print(datetime.utcnow(),
                  "okes,全部成交,订单ID:{},成交均价:{}".format(orderId, priceAvg))
        elif state_info == "1":
            print(datetime.utcnow(), "okes,部分成交需撤单,订单ID:{}".format(orderId))
            try:
                result_order_cancel = \
                    self.futureAPI.revoke_order(
                        self.symbol_okex, order_id=orderId)
            except OkexAPIException as e:
                print('撤单', e.code, e.message)
                if e.code == 30003:
                    return {'code': -1}
                else:
                    raise e
            if not result_order_cancel['result']:
                print("okes,撤单失败", result_order_cancel['error_code'],
                      result_order_cancel['error_message'])
                result['code'] = -1
                return result
            else:
                result['code'] = 0
                self.VOLUME_TMP = size - filledQty
                print("okes,部分成交已撤单,剩余{}张,订单ID:{}".format(self.VOLUME_TMP,
                      orderId))
        elif state_info == '0':
            # 撤单
            print("okes,等待成交需撤单,订单ID:{}".format(orderId))
            try:
                result_order_cancel = \
                    self.futureAPI.revoke_order(
                        self.symbol_okex, order_id=orderId)
            except OkexAPIException as e:
                print('撤单', e.code, e.message)
                if e.code == 30003:
                    return {'code': -1}
                else:
                    raise e
            if (not result_order_cancel['result'] or
                    result_order_cancel.get('error_message') or
                    result_order_cancel.get('error_code')):
                result['code'] = -1
                print("okes,撤单失败", result_order_cancel['error_code'],
                      result_order_cancel['error_message'])
            elif result_order_cancel['result']:
                print("okes,撤单成功，orderId:{}".format(orderId))
                result['code'] = 0

        if filledQty:
            if otype == '1' or otype == '4':
                self.pos['pos_okex'] += filledQty
            elif otype == '2' or otype == '3':
                self.pos['pos_okex'] -= filledQty
        return result

    def parse_huobi(self, result_origin):
        time.sleep(0.5)
        # code 0.失败 1.成功 2.部分成功 -1.撤单失败
        # status, ok|error
        # 假设以对手价下单,未成交即撤单
        result = dict()
        if result_origin['status'] == 'ok':
            orderId = result_origin['data']['order_id']
            result_info = self.dm.get_contract_order_info(
                "BTC", order_id=orderId)
            if 'data' not in result_info.keys():
                print('huobi,订单信息查询失败，status:{}'.format(
                      result_info.get('status')))
                return {'code': -1}
            info = result_info['data'][0]
            # 委托数量
            volume = info['volume']
            # "buy":买 "sell":卖
            direction = info['direction']
            # "open":开 "close":平
            offset = info['offset']
            # 成交数量
            trade_volume = info['trade_volume']
            # 成交均价
            priceAvg = info['trade_avg_price']
            # (1准备提交 2准备提交 3已提交 4部分成交 5部分成交已撤单 6全部成交 7已撤单 11撤单中)
            status = info['status']

            result['code'] = 1

            print("huobi订单返回status:{}".format(status))
            if status == 6:
                print(datetime.utcnow(),
                      "huobi,全部成交,订单ID:{},成交均价:{}".format(orderId, priceAvg))
            elif status == 3:
                time.sleep(0.5)
                print(datetime.utcnow(),
                      "huobi,已提交还未成交需撤单,订单ID:{}".format(orderId))
                result_order_cancel = \
                    self.dm.cancel_contract_order('BTC', order_id=orderId)
                if (result_order_cancel['status'] == 'ok'
                        and result_order_cancel['data'].get('successes')
                        and orderId ==
                        int(result_order_cancel['data']['successes'])):
                    print(datetime.utcnow(),
                          "huobi,撤单成功,订单ID:{}".format(orderId))
                    result['code'] = 0
                else:
                    result['code'] = -1
                    for error in result_order_cancel['data']['errors']:
                        if error['order_id'] == orderId:
                            print(
                                datetime.utcnow(),
                                "huobi,撤单失败,订单ID:{},err_code:{},err_msg:{}".
                                format(orderId, error['err_code'],
                                       error['error']))
            elif status < 5:
                result['code'] = -1
            elif status == 5:
                result['code'] = 0
                self.VOLUME_TMP = volume - trade_volume
                print("huobi,部分成交已撤单,剩余{}张,订单ID:{}".format(
                    self.VOLUME_TMP, orderId))

            if direction == 'buy' and offset == 'close':
                self.pos['pos_huobi'] += trade_volume
            elif direction == 'sell' and offset == 'close':
                self.pos['pos_huobi'] -= trade_volume
        else:
            result['code'] = 0

        return result

    def close_huobi(self, p, mp):
        if self.pos['pos_huobi'] > 0:
            r = self.dm.send_contract_order(
                symbol=self.symbol_huobi, contract_type='quarter',
                contract_code='', client_order_id='',
                price=None, volume=self.pos['pos_huobi'],
                direction='sell', offset='close',
                lever_rate=self.LEVERAGE, order_price_type='opponent')
        elif self.pos['pos_huobi'] < 0:
            r = self.dm.send_contract_order(
                symbol=self.symbol_huobi, contract_type='quarter',
                contract_code='', client_order_id='', price=None,
                volume=abs(self.pos['pos_huobi']), direction='buy',
                offset='close', lever_rate=self.LEVERAGE,
                order_price_type='opponent')
        else:
            return {'code': 1}
        result = self.parse_huobi(r)
        while result['code'] == -1:
            result = self.parse_huobi(r)
        return result

    def close_okex(self, p, mp):
        instrument_id = self.symbol_okex
        price = p
        match_price = mp
        result = dict()
        if self.pos['pos_okex'] > 0:
            otype = 3
            r = self.futureAPI.take_order(
                instrument_id, otype, price, self.pos['pos_okex'],
                match_price, self.LEVERAGE)
        elif self.pos['pos_okex'] < 0:
            otype = 4
            r = self.futureAPI.take_order(
                instrument_id, otype, price, abs(self.pos['pos_okex']),
                match_price, self.LEVERAGE)
        else:
            return {'code': 1}
        result = self.parse_okex(r)
        while result['code'] == -1:
            result = self.parse_okex(r)
        return result

    def buy_huobi(self, p, mp):
        volume = self.VOLUME_TMP if self.VOLUME_TMP else self.VOLUME
        r = self.dm.send_contract_order(
            symbol=self.symbol_huobi, contract_type='quarter',
            contract_code='', client_order_id='', price=None,
            volume=volume,
            direction='buy', offset='open',
            lever_rate=self.LEVERAGE, order_price_type='opponent')
        self.pos['pos_huobi'] += volume
        result = self.parse_huobi(r)
        while result['code'] == -1:
            result = self.parse_huobi(r)
        if result['code'] == 0:
            self.pos['pos_huobi'] -= volume
        return result

    def sell_huobi(self, p, mp):
        volume = self.VOLUME_TMP if self.VOLUME_TMP else self.VOLUME
        r = self.dm.send_contract_order(
            symbol=self.symbol_huobi, contract_type='quarter',
            contract_code='', client_order_id='', price=None,
            volume=volume,
            direction='sell', offset='open',
            lever_rate=self.LEVERAGE, order_price_type='opponent')
        self.pos['pos_huobi'] -= volume
        result = self.parse_huobi(r)
        while result['code'] == -1:
            result = self.parse_huobi(r)
        if result['code'] == 0:
            self.pos['pos_huobi'] += volume
        return result

    def buy_okex(self, p, mp):
        #   take_order(self, instrument_id, otype, price, size,
        #       match_price, leverage, client_oid=None):
        #   otype, 1:开多2:开空3:平多4:平空
        #   match_price,是否以对手价下单(0:不是 1:是)
        instrument_id = self.symbol_okex
        otype = 1
        price = p
        match_price = mp
        result = dict()
        r = self.futureAPI.take_order(
            instrument_id, otype, price,
            self.VOLUME_TMP if self.VOLUME_TMP else self.VOLUME,
            match_price, self.LEVERAGE)
        result = self.parse_okex(r)
        while result['code'] == -1:
            result = self.parse_okex(r)
        return result

    def sell_okex(self, p, mp):
        instrument_id = self.symbol_okex
        otype = 2
        price = p
        match_price = mp
        result = dict()
        r = self.futureAPI.take_order(
            instrument_id, otype, price,
            self.VOLUME_TMP if self.VOLUME_TMP else self.VOLUME,
            match_price, self.LEVERAGE)
        result = self.parse_okex(r)
        while result['code'] == -1:
            result = self.parse_okex(r)
        return result
