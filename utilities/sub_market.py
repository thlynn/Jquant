import threading
import gzip
import json
from websocket import create_connection
from Jquant.utilities.tools import inflate
from datetime import datetime
from datetime import timedelta


class P_OKEX(threading.Thread):

    def __init__(self, name):
        super().__init__(name=name)
        self.timestamp = None
        self.close = None
        self.ws_okex = create_connection("wss://real.okex.com:8443/ws/v3")

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

    def __init__(self, name):
        super().__init__(name=name)
        self.timestamp = None
        self.close = None
        self.ws_huobi = create_connection("wss://www.hbdm.com/ws")

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
                tick = jsonObj['tick']
                timestamp = datetime.utcfromtimestamp(
                    tick['id'])
                self.timestamp = timestamp
                self.close = tick['close']
