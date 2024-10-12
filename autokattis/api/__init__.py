from abc import ABC, abstractmethod

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

from .databasemanager import DatabaseManager
from .loginmanager import LoginManager
from .utils import suppress_warnings

class ABCKattis(ABC):
    class Result(list):
        def __init__(self, data):
            super().__init__(data)
            self.to_df = lambda: pd.DataFrame(data)

    def __init__(self, base_url, username, password):
        suppress_warnings()
        self.session = requests.Session()
        self.session.__init__()
        self.base_url = base_url
        self.homepage = ''
        self.max_workers = 6
        self.username = LoginManager(self).login(username, password)
        self.db = DatabaseManager(self)

    def new_get(self, *args, **kwargs):
        try:    return self.session.get(*args, **kwargs)
        except: return self.new_get(*args, **kwargs)

    def new_post(self, *args, **kwargs):
        try:    return self.session.post(*args, **kwargs)
        except: return self.new_post(*args, **kwargs)

    def get_base_url(self):
        return self.base_url

    def get_homepage(self):
        return self.homepage

    def set_homepage(self, hp):
        self.homepage = hp

    def get_session(self):
        return self.session

    def get_max_workers(self):
        return self.max_workers

    def get_username(self):
        return self.username

    def get_database(self):
        return self.db

    def get_soup_response(self, url):
        response = self.new_get(url)
        return bs(response.content, features='lxml')

    def load_homepage(self):
        self.set_homepage(self.get_soup_response(self.get_base_url()))

    @abstractmethod
    def problems(self, **configs):
        pass

    @abstractmethod
    def problem(self, problem_ids, download_files, *args):
        pass

    @abstractmethod
    def stats(self, languages, *args):
        pass
