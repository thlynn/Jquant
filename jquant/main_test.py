import pandas as pd

from app_private.rsi.rsi_run_back_test import RSIRunBackTest


if __name__ == "__main__":
    bars = pd.read_csv('huobi_future_data_1year.csv')
    init_bars = bars.iloc[:3600]
    back_test_bars = bars.iloc[3600:]

    test = RSIRunBackTest('BTC', 5, '15min', init_bars)
    df = test.proceed_back_test(back_test_bars)

    df.to_csv('/var/back_test_result/results.csv')

