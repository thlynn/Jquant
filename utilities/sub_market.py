import threading
import gzip
import json
from websocket import create_connection
from utilities.tools import inflate
from datetime import datetime


class SubscribeOKEXFuture(threading.Thread):

    def __init__(self, name):
        super().__init__(name=name)
        self.timestamp = None
        self.close = None
        self.ws_url = create_connection("wss://real.okex.com:8443/ws/v3")

    def run(self):
        while True:
            result = inflate(self.ws_okex.recv())
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


class SubscribeHUOBIFuture(threading.Thread):

    def __init__(self, name):
        super().__init__(name=name)
        self.timestamp = None
        self.close = None
        self.ws_url = create_connection("wss://www.hbdm.com/ws")

    def run(self):
        while True:
            result = gzip.decompress(self.ws_huobi.recv()).decode('utf-8')
            json_obj = json.loads(result)
            if json_obj.get('status') == 'error':
                pass
            elif 'ping' in json_obj.keys():
                pong = '{"pong":'+str(json_obj['ping'])+'}'
                self.ws_url.send(pong)
            elif 'ch' in json_obj.keys():
                tick = json_obj['tick']
                timestamp = datetime.utcfromtimestamp(
                    tick['id'])
                self.timestamp = timestamp
                self.close = tick['close']


class SubscribeHUOBI(threading.Thread):

    def __init__(self, name):
        super().__init__(name=name)
        self.timestamp = None
        self.close = None
        self.ws_url = create_connection("wss://www.hbdm.com/ws")

    def run(self):
        while True:
            result = gzip.decompress(self.ws_huobi.recv()).decode('utf-8')
            json_obj = json.loads(result)
            if json_obj.get('status') == 'error':
                pass
            elif 'ping' in json_obj.keys():
                pong = '{"pong":'+str(json_obj['ping'])+'}'
                self.ws_url.send(pong)
            elif 'ch' in json_obj.keys():
                tick = json_obj['tick']
                timestamp = datetime.utcfromtimestamp(
                    tick['id'])
                self.timestamp = timestamp
                self.close = tick['close']


class SubscribeHUOBI(threading.Thread):

    def __init__(self, name):
        super().__init__(name=name)
        self.timestamp = None
        self.close = None
        self.ws_url = create_connection("wss://www.hbdm.com/ws")

    def run(self):
        while True:
            result = gzip.decompress(self.ws_huobi.recv()).decode('utf-8')
            json_obj = json.loads(result)
            if json_obj.get('status') == 'error':
                pass
            elif 'ping' in json_obj.keys():
                pong = '{"pong":'+str(json_obj['ping'])+'}'
                self.ws_url.send(pong)
            elif 'ch' in json_obj.keys():
                tick = json_obj['tick']
                timestamp = datetime.utcfromtimestamp(
                    tick['id'])
                self.timestamp = timestamp
                self.close = tick['close']

