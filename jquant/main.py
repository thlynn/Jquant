import itertools
import multiprocessing
import os
import time
from datetime import datetime, timedelta
import pandas as pd

from app_private.turtle.turtle_run import TurtleRun
from app_private.turtle.turtle_run_back_test import TurtleRunBackTest
from data.huobi_candlesticks import HUOBIFutureHistory

# os.environ['HTTP_PROXY'] = "http://127.0.0.1:1082"
# os.environ['HTTPS_PROXY'] = "https://127.0.0.1:1082"


def run_back_test(entry_, exit_, atr_):
    run = TurtleRunBackTest('BTC', 'USDT', 5, '1min', entry_, exit_, atr_)
    return run.proceed()


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
    # run = TurtleRun('BTC', 'USDT', 5, '1min')

    # entry_window = (40, 100, 5)
    # exit_window = (10, 40, 5)
    # atr_window = (20, 100, 10)

    entry_window = (40, 50, 5)
    exit_window = (10, 20, 5)
    atr_window = (20, 40, 10)

    test_list = [range(*entry_window), range(*exit_window), range(*atr_window)]

    processes = [multiprocessing.Process(target=run_back_test, args=i) for i in list(itertools.product(*test_list))]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    print([p.get() for p in processes])
