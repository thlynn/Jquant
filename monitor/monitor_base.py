import threading

from core.logger import get_logger


class MonitorBase(threading.Thread):

    def __init__(self) -> None:
        super().__init__()
        self.logger = get_logger('Monitor')
