import configparser
from utilities.tools import get_host_ip
import os


class Keys():
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath(__file__)) + '/key.ini', encoding='utf-8')

    ip = get_host_ip()

    URL = config['HUOBI']['URL']
    ACCESS_KEY = config['HUOBI_{}'.format(ip)]['ACCESS_KEY']
    SECRET_KEY = config['HUOBI_{}'.format(ip)]['SECRET_KEY']

    api_key = config['OKEX_{}'.format(ip)]['ACCESS_KEY']
    seceret_key = config['OKEX_{}'.format(ip)]['SECRET_KEY']
    passphrase = config['OKEX']['PASSPHRASE']
