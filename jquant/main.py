
from app.turtle.turtle_run import TurtleRun


if __name__ == "__main__":
    # os.environ['HTTP_PROXY'] = "http://127.0.0.1:1082"
    # os.environ['HTTPS_PROXY'] = "https://127.0.0.1:1082"

    run = TurtleRun('BTC', 'USDT', 5, '60min')
    run.proceed()
