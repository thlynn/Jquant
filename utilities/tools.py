import zlib
import socket
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
    return up[-2], down[-2]


def atr(n, df):
    """
    Average True Range (ATR).
    """
    result = talib.ATR(df.high_price, df.low_price, df.close_price, n)
    return result[-2]