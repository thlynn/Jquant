import os
import time
from datetime import datetime, timedelta
import pandas as pd

from app_private.turtle.turtle_run import TurtleRun
from app_private.turtle.turtle_run_back_test import TurtleRunBackTest
from data.huobi_candlesticks import HUOBIFutureHistory

# os.environ['HTTP_PROXY'] = "http://127.0.0.1:1082"
# os.environ['HTTPS_PROXY'] = "https://127.0.0.1:1082"


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
    df.to_csv('data/csv/huobi_future_test_7days.csv')


if __name__ == "__main__":

    # get_huobi_future_data()

    base_symbol = 'BTC'
    quote_symbol = 'USDT'
    pos = 5
    intervals = '1min'

    run = TurtleRunBackTest(
        base_symbol, quote_symbol, pos, intervals,
        '/var/csv/huobi_future_test_7days.csv', '/var/back_test_result/back_test_results_entry_Test_4.csv')

    # run = TurtleRun(base_symbol, quote_symbol, pos, intervals)

    run.proceed()

