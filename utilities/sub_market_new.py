import threading
import gzip
import json
from websocket import create_connection
from Jquant.utilities.tools import inflate
from Jquant.model.BaseModel import Tick
from datetime import datetime


class P_OKEX(threading.Thread):

    def __init__(self, name, callback):
        super().__init__(name=name)
        self.timestamp = None
        self.close = None
        self.ws_okex = create_connection("wss://real.okex.com:8443/ws/v3")
        self.callback = callback

    def run(self):
        while True:
            result = inflate(self.ws_okex.recv())
            if result == b'pong':
                pass
            else:
                jsonObj = json.loads(result)
                if('data' in jsonObj.keys()):
                    data = jsonObj['data'][0]
                    candle = data['candle']
                    timestamp = datetime.strptime(
                        candle[0], '%Y-%m-%dT%H:%M:%S.%fZ')
                    self.timestamp = timestamp
                    if candle[4]:
                        self.close = float(candle[4])
                    if (not self.timestamp or
                            self.timestamp.minute != timestamp.minute):
                        self.ws_okex.send('ping')


class P_HUOBI(threading.Thread):

    def __init__(self, name, callback):
        super().__init__(name=name)
        self.ws_huobi = create_connection("wss://www.hbdm.com/ws")
        self.callback = callback

    def run(self):
        while True:
            result = gzip.decompress(self.ws_huobi.recv()).decode('utf-8')
            jsonObj = json.loads(result)
            if(jsonObj.get('status') == 'error'):
                pass
            elif('ping' in jsonObj.keys()):
                pong = '{"pong":'+str(jsonObj['ping'])+'}'
                self.ws_huobi.send(pong)
            elif('ch' in jsonObj.keys()):
                obj = Tick()
                tick = jsonObj['tick']
                obj.timestamp = tick['id']
                obj.volume = tick['vol']
                obj.open_price = tick['open']
                obj.high_price = tick['high']
                obj.low_price = tick['low']
                obj.close_price = tick['close']
                self.callback(obj)
