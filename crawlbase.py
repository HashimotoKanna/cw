from abc import ABC, abstractmethod
import os
import codecs
from functools import reduce

from bs4 import BeautifulSoup
import requests

get = lambda *args, **kwargs: requests.get(*args, **kwargs)
getsoup = lambda url: BeautifulSoup(get(url).text,'html.parser')
str2tag = lambda str: BeautifulSoup(str).find()
tag2str = lambda tag: str(tag)
getpath = lambda *path: os.path.join(*path)
join = lambda *args: reduce(lambda x,y:x+y, args)

def makedir(title, subtitle):
    dir = os.path.join( os.path.dirname(__file__), title, subtitle )
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def savefile(file, data, utf8=False):
    if utf8:
        with codecs.open(file, 'w', 'utf-8') as f:
            f.write(data)
    else:
        with open(file, 'wb') as f:
            f.write(data)

class CrawlBase(ABC):
    # @staticmethod
    # def get(*args, **kwargs):
    #     return requests.get(*args, **kwargs)
    # @staticmethod
    # def getsoup(url):
    #     return BeautifulSoup(requests.get(url).text, 'html.parser')
    # @staticmethod
    # def str2tag(str):
    #     return BeautifulSoup(str).find()
    # @staticmethod
    # def tag2str(tag):
    #     return str(tag)
    # @staticmethod
    # def getpath(*path)
    #     return os.path.join(*path)
    # @staticmethod
    # def join(*args):
    #     return reduce(lambda x,y: x+y, *args)

    @abstractmethod
    def crawl(self):
        pass
        
    @abstractmethod
    def doit(self):
        pass

