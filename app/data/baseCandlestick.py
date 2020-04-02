import json
from abc import ABC, abstractmethod

import requests

from model.BaseModel import EnhancedJSONEncoder


class BaseCandlestick(ABC):

    def __init__(self, base_symbol, quote_symbol, intervals):
        self.base_symbol = base_symbol
        self.quote_symbol = quote_symbol
        self.intervals = intervals
        self.req_str = ''
        self.bars = list()
        super().__init__()

    def req_data(self):
        res = requests.get(self.req_str)
        data = json.loads(res.content)['data']
        return data

    @abstractmethod
    def parse_data(self, data):
        pass

    def to_json(self):
        return json.dumps(self.bars, cls=EnhancedJSONEncoder)
