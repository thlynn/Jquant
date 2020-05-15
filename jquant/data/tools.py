import zlib
import socket
from decimal import Decimal

import talib


def inflate(data):
    decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
    )
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def donchian(n, df):
    """
    Donchian Channel.
    """
    up = talib.MAX(df.high_price, n)
    down = talib.MIN(df.low_price, n)
    return Decimal(str(up[-2])), Decimal(str(down[-2]))


def atr(n, df):
    """
    Average True Range (ATR).
    """
    result = talib.ATR(df.high_price, df.low_price, df.close_price, n)
    return Decimal(str(result[-2]))


def calculate_pos_and_average_price(pos, average_price, volume, price):
    pos = Decimal(str(pos))
    volume = Decimal(str(volume))

    average_price = (pos * average_price + volume * price)/(pos + volume)
    return int(pos + volume), average_price
