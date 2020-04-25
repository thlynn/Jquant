import threading


class MonitorBase(threading.Thread):

    def __init__(self) -> None:
        super().__init__()
