import json

from datetime import datetime
from datetime import timedelta
from websocket import create_connection

from data.subscribe import Subscribe
from data.tools import inflate
from model.BaseModel import Bar, Exchange
import api.okex.futures_api as future
from config import Keys


class OKExData(object):
    '''
    k线数据最多可获取最近2880条
    时间粒度granularity必须是[60 180 300 900 1800 3600 7200 14400
        21600 43200 86400 604800]中的任一值，否则请求将被拒绝。
        这些值分别对应的是[1min 3min 5min 15min 30min 1hour 2hour 4hour
        6hour 12hour 1day 1week]的时间段。
    未提供开始时间和结束时间的请求，则系统按时间粒度返回最近的200个数据
    限速规则：20次/2s
    单次请求的最大数据量是300
    UTC时间 相差8个小时
    '''

    futureAPI = future.FutureAPI(
        Keys.api_key, Keys.seceret_key, Keys.passphrase, True)

    def __init__(self, symbol, period, begin: datetime, end: datetime):
        # SYMBOL = 'BTC-USD-190927'
        # period = 60
        super().__init__()
        self.symbol = symbol
        self.begin = begin
        self.end = end
        self.interval = 300
        self.period = period

    def main(self):
        result = list()
        begin = self.begin
        end = self.begin + timedelta(minutes=self.interval)
        period = 0
        if self.period == '1min':
            period = 60
        while True:
            print(begin, '-', end)
            rsp = self.futureAPI.get_kline(
                self.symbol, period,
                start=datetime.strftime(begin, '%Y-%m-%dT%H:%M:%SZ'),
                end=datetime.strftime(end, '%Y-%m-%dT%H:%M:%SZ'))
            bars = self.parse_data(rsp)
            result.extend(bars)
            if end >= self.end:
                break
            begin = end
            end = begin + timedelta(minutes=self.interval)
        return result

    def parse_data(self, data):
        bars = list()
        for arr in data:
            bar = Bar()
            bar.timestamp = datetime.timestamp(
                datetime.strptime(arr[0]+'+0000', '%Y-%m-%dT%H:%M:%S.%fZ%z'))
            bar.symbol = self.symbol
            bar.period = self.period
            bar.exchange = Exchange.OKEX.name
            bar.volume = float(arr[5])
            bar.open_price = float(arr[1])
            bar.close_price = float(arr[4])
            bar.high_price = float(arr[2])
            bar.low_price = float(arr[3])
            bars.append(bar.__dict__)
        return bars


class SubscribeOKEXFuture(Subscribe):

    def __init__(self, base_symbol, quote_symbol, intervals, callback=None):
        super().__init__(base_symbol, quote_symbol, intervals, callback)
        self.ws_url = create_connection("wss://real.okex.com:8443/ws/v3")

    def run(self):
        while True:
            result = inflate(self.ws_url.recv())
            if result == b'pong':
                pass
            else:
                json_obj = json.loads(result)
                if 'data' in json_obj.keys():
                    data = json_obj['data'][0]
                    candle = data['candle']
                    timestamp = datetime.strptime(
                        candle[0], '%Y-%m-%dT%H:%M:%S.%fZ')
                    self.timestamp = timestamp
                    if candle[4]:
                        self.close = float(candle[4])
                    if (not self.timestamp or
                            self.timestamp.minute != timestamp.minute):
                        self.ws_url.send('ping')
