import configparser
import os


class Keys():
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath(__file__)) + '/key.ini', encoding='utf-8')

    URL = config['HUOBI']['URL']
    ACCESS_KEY = config['HUOBI']['ACCESS_KEY']
    SECRET_KEY = config['HUOBI']['SECRET_KEY']

    api_key = config['OKEX']['ACCESS_KEY']
    seceret_key = config['OKEX']['SECRET_KEY']
    passphrase = config['OKEX']['PASSPHRASE']
