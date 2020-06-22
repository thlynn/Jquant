import time

from datetime import datetime, timedelta
import pandas as pd

from data.huobi import HUOBIFutureHistory


def get_huobi_future_data():
    base_time = datetime.strptime('2020-05-13', '%Y-%m-%d')
    last_year = base_time - timedelta(days=7)
    begin = int(datetime.timestamp(last_year))
    end = int(datetime.timestamp(base_time))
    to = begin + 2000 * 60

    history = HUOBIFutureHistory('BTC', 'USDT')

    bars = list()
    if begin and end:
        while to < end:
            print(f'{begin}----{to}')
            try:
                response_data = history.req_data_by_time_range(begin, to)
            except Exception as e:
                print(e)
                continue
            bars.extend(history.construct(response_data))
            begin = to
            to += 2000 * 60
            time.sleep(1)

    df = pd.DataFrame(data=[bar.__dict__ for bar in bars])
    df.to_csv('data/csv/huobi_future_test_1year.csv')
