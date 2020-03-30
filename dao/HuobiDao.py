from pymongo import MongoClient
from datetime import datetime


class HuobiDao(object):

    def __init__(self):
        super().__init__()
        self.client = MongoClient()
        db = self.client.Jquant
        self.collection = db.huobi

    def get_data(self, symbol, period, begin, end):
        result = list()
        cur_huobi = self.collection.find({
            "symbol": symbol,
            "period": period,
            "timestamp": {"$gte": begin, "$lte": end}
        })
        for obj in cur_huobi:
            obj['timestamp'] = datetime.utcfromtimestamp(obj['timestamp'])
            result.append(obj)
        return result
