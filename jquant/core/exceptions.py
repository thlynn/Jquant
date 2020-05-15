class Error(Exception):
    pass


class OrderHasBeenCreatedError(Error):
    pass


class APIError(Error):

    def __init__(self, message):
        self.message = message


class TimestampError(Error):
    pass
