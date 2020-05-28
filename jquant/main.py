import itertools
import multiprocessing
import os
import time
from datetime import datetime, timedelta
import pandas as pd

from app_private.rsi.rsi_run import RSIRun
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


bars = pd.read_csv('/var/csv/huobi_future_test_365days.csv')
init_bars = bars.iloc[:2000]
back_test_bars = bars.iloc[2000:]

def run_back_test(attrs):
    run = TurtleRunBackTest('BTC', 'USDT', 5, '1min', attrs[0], attrs[1], attrs[2 ], init_bars)
    print(run.proceed_back_test(back_test_bars))


if __name__ == "__main__":
    # run = TurtleRun('BTC', 'USDT', 5, '1min')

    run = RSIRun('BTC', 'USDT', 1, '1min')
    run.proceed()

    # entry_window = (40, 100, 5)
    # exit_window = (10, 40, 5)
    # atr_window = (20, 100, 10)
    #
    # test_list = [range(*entry_window), range(*exit_window), range(*atr_window)]
    #
    # with multiprocessing.Pool(5) as p:
    #     print(p.map(run_back_test, list(itertools.product(*test_list))))
