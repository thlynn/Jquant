import configparser
import os


class Keys:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.dirname(os.path.abspath(__file__)) + '/key.ini', encoding='utf-8')

    def get_key(self, name):
        access_key = self.config[name]['ACCESS_KEY']
        secret_key = self.config[name]['SECRET_KEY']
        return access_key, secret_key

    def get_base_url(self, name):
        url = self.config[name]['URL']
        return url
