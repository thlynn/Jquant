import json
import gzip
import time
from datetime import datetime
from websocket import create_connection
from model.BaseModel import Bar, Exchange
from api.huobi.HuobiDMService import HuobiDM
from config import Keys


class HuoBiData(object):

    url = "wss://www.hbdm.com/ws"

    def __init__(self):
        super().__init__()
        self.ws = create_connection(self.url)

    def ws_data(self, symbol, period, b: int, e: int):

        b = int(b)
        e = int(e)
        if period == '1min':
            interval = 299*60

        result = list()
        begin = b
        end = begin + interval
        flag = 1
        while True:
            if flag:
                jsonObj = self.req_data(begin, end, symbol, period)
            compressData = self.ws.recv()
            jsonStr = gzip.decompress(compressData).decode('utf-8')
            jsonObj = json.loads(jsonStr)
            if(jsonObj.get('status') == 'error'):
                err = jsonObj['err-msg']
                if err.startswith('429 too many request topic is'):
                    time.sleep(2)
                else:
                    print(jsonObj['err-msg'])
            elif('ping' in jsonObj.keys()):
                pong = '{"pong":' + str(jsonObj['ping']) + '}'
                self.ws.send(pong)
                flag = 0
                print(pong)
            else:
                data = jsonObj['data']
                if data:
                    print(datetime.fromtimestamp(begin), '-',
                          datetime.fromtimestamp(end))
                    bars = self.parse_data(data, symbol, period)
                    result.extend(bars)
                    if((data[-1]['id'] == end) or
                       (data[0]['id'] == begin)):
                        if end >= e:
                            break
                        begin = end
                        end = begin + interval
                        if end > e:
                            end = e
                        flag = 1
                    else:
                        flag = 0
                else:
                    print('空数据')
                    flag = 1
        return result

    def parse_data(self, data, symbol, period):
        bars = list()
        for obj in data:
            bar = Bar()
            bar.timestamp = obj['id']
            bar.symbol = symbol
            bar.period = period
            bar.exchange = Exchange.HUOBI.name
            bar.volume = obj['amount']
            bar.open_price = obj['open']
            bar.close_price = obj['close']
            bar.high_price = obj['high']
            bar.low_price = obj['low']
            bars.append(bar.__dict__)
        return bars

    def req_data(self, begin, end, symbol, period):
        reqstr = "market.{}.kline.{}".format(symbol, period)
        tradeObj = {"req": reqstr, "id": "id10", "from": begin, "to": end}
        tradeStr = json.dumps(tradeObj)
        self.ws.send(tradeStr)

    def get_data(self, symbol, period):
        # 非利用WS，直接获取最近两千条数据
        dm = HuobiDM(Keys.URL, Keys.ACCESS_KEY, Keys.SECRET_KEY)
        jsonObj = dm.get_contract_kline(symbol, period, 2000)
        return self.parse_data(jsonObj['data'], symbol, period)
