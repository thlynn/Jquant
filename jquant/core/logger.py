import logging
import sys
from logging.handlers import RotatingFileHandler
import os

FORMATTER = logging.Formatter("%(asctime)s — %(threadName)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler(file_name):
    direction = '/var/log'
    os.makedirs(direction, exist_ok=True)
    file_handler = RotatingFileHandler(f'{direction}/{file_name}.log', mode='w', maxBytes=5000000, backupCount=2)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
    # logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(logger_name))
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
