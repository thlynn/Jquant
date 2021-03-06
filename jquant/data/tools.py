import zlib
import socket
from decimal import Decimal
import numpy as np

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


def donchian(n, bars):
    """
    Donchian Channel.
    """
    up = talib.MAX(bars['high'], n)
    down = talib.MIN(bars['low'], n)
    return Decimal(str(up[-2])), Decimal(str(down[-2]))


def donchian_array(n, bars):
    """
    Donchian Channel.
    """
    up = talib.MAX(bars['high'], n)
    down = talib.MIN(bars['low'], n)
    return up, down


def atr(n, bars):
    """
    Average True Range (ATR).
    """
    result = talib.ATR(bars['high'], bars['low'], bars['close'], n)
    return Decimal(str(result[-2]))


def rsi(n, bars):
    result = talib.RSI(bars['close'], timeperiod=n)
    return result[-1]


def rsi_array(n, bars):
    result = talib.RSI(bars['close'], timeperiod=n)
    return result


def calculate_pos_and_average_price(pos, average_price, volume, price):
    pos = Decimal(str(pos))
    volume = Decimal(str(volume))

    average_price = (pos * average_price + volume * price)/(pos + volume)
    return int(pos + volume), average_price
