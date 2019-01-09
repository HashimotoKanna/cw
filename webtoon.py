# -*- coding: utf-8 -*-

from sys import stderr
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

def savefile(file, data, utf8 = False):
    if utf8:
        with codecs.open(file, 'w', 'utf-8') as f:
            f.write(data)
    else:
        with open(file, 'wb') as f:
            f.write(data)

class CrawlBase(ABC):
    @abstractmethod
    def crawl(self):
        pass
        
    @abstractmethod
    def doit(self):
        pass

class InvalidURL(requests.exceptions.MissingSchema):
    pass
class EmptyContent(Exception):
    pass

def error_print(type, url_target):
    stderr.write('%s IS EMPTY\n' % type)
    stderr.write('URL TARGET : '+url_target['href'])
    stderr.write('URL NAME : '+url_target.text)
                

class MarumaruCrawl(CrawlBase):
    ROOT = 'http://wasabisyrup.com'

    ATTEMPT_IF_FAILED = 5
    JPEG_MAGIC_NUMBER = b'\xff\xd8\xff\xe0'

    def __init__(self, target, name):
        soup = getsoup(target)
        self.index = soup.select('#vContent a')
        self.failed = {'msg':str(), 'lst':list()}

    def doit(self):
        for i, idx in enumerate(self.index):
            self.crawl(idx)
        with open('fail_log.txt', 'w') as f:
            fail = self.failed['msg']
            fail += '\n\n'
            for src in self.failed['lst']:
                fail += src + '\n'
            f.write(fail)

    def crawl(self, url_target):
        try:
            soup = getsoup(url_target['href'])
            titles = soup.select('.title-text span')
            imgs = soup.select('.article-gallery img')

            if not titles:
                error_print('TITLES', url_target)
                raise EmptyContent
            if not imgs:
                error_print('IMAGE TAGS', url_target)
                raise EmptyContent
        except InvalidURL:
            return
        except EmptyContent:
            return
        else:

            title = titles[0].text
            subtitle = titles[1].text
            dir = makedir(title, subtitle)

            for i, img in enumerate(imgs):
                if i < 10:
                    filename = getpath(dir, '00'+repr(i)+'.jpeg')
                elif 10 <= i < 100:
                    filename = getpath(dir, '0'+repr(i)+'.jpeg')
                else:
                    filename = getpath(dir, repr(i)+'.jpeg')

                for _ in range(self.ATTEMPT_IF_FAILED):
                    src = self.ROOT + img['data-src']
                    jpeg = get(src).content
                    if jpeg[:4] == self.JPEG_MAGIC_NUMBER:
                        break
                    print(title, subtitle, i, '번째 이미지 크롤 실패 재시도...')
                else:
                    print(title, subtitle, i, '번째 이미지 크롤 실패...')                
                    self.failed['msg'] += ' '.join((title, subtitle, repr(i), '번쨰 이미지\n'))
                    self.failed['lst'].append(src)
                    continue
                savefile(filename, jpeg)
                
                percentage = round(i / len(imgs) * 100)
                msg = ' '.join((
                        title, subtitle, '크롤링 중..', repr(percentage), '%', '\r'
                ))
                print(msg)
            print('')

class NaverCrawl(CrawlBase):
    ROOT = 'http://comic.naver.com/webtoon/detail.nhn'

    def __init__(self, target, name):
        from urllib.parse import urlparse
        url = urlparse(target)
        info = dict((param.split('=') for param in url.query.split('&')))

        self.name = name
        self.titleId = info['titleId']
        self.latest = int(info['no'])
        self.index = [repr(i) + '화' for i in range(1, self.latest + 1)]

    def doit(self, update = 0):
        if update:
            for no in range(update, self.latest + 1):
                self.crawl(self.titleId, no)
        else:
            for no in range(1, self.latest + 1):
                self.crawl(self.titleId, no)
        self.indexing()

    def crawl(self, titleId, no):
        url = join( self.ROOT, '?', 'titleId=', titleId, '&no=', str(no) )
        soup = getsoup(url)

        subtitle = str(no)+'화'

        dir = makedir(self.name, subtitle)
        
        imgs = soup.select('.wt_viewer img')

        for i, tag in enumerate(imgs):
            filename = getpath(dir, repr(i+1)+'.jpg')

            jpg = get(tag['src'], headers = {'Referer' : url}).content
            savefile(filename, jpg)

        self.htmling(subtitle, len(imgs), dir)
        msg = ' '.join((self.name, subtitle, '크롤링 완료'))
        print(msg)

    def indexing(self):
        getatag = lambda NAME: '<a href="{name}/{name}.html">{name}</a><br>'.format(name=NAME)
        
        head = '<html><head><title>'+self.name+'</title><style>*{background-color:black} body{text-align: center;}</style></head>'
        '<body><h1>'+self.name+'</h1>'
        tail = '</body></html>' 

        atags = ''.join(getatag(idx)+'\n' for idx in self.index)
        html = join(head, atags, tail)

        from os import chdir
        chdir(self.name)
        savefile(self.name+'.html', html, utf8=True)

    def htmling(self, title, imgct, dir):
        head = '<html><head><title>'
        body = '''</title><style>
                    * {background-color: black;}
                    body {color: #434343;
                        height: 100%;
                        margin: 0;}
                    #wrap{position: relative;
                        width: 960px;
                        height: 100%;
                        margin: 0 auto;}
                    .viewer{min-width: 960px;
                        padding: 50px 0;
                        text-align: center;
                        font-size: 0;
                        line-height: 0;}
                    img {vertical-align: top;
                        display: block;
                        margin: 0 auto;
                        border: 0;}
                    h1{text-align: center;
                        color: lightcoral;}
        </style></head><body><div id="wrap"><div id="wrap" class="viewer"> '''
        img_tags = ['<img src="'+str(i)+'.jpg"/>' for i in range(1, imgct + 1)]
        tail = '</div></div></body></html>'
            
        filename = getpath(dir, title+'.html')
        
        html = join(head, title, body, *img_tags, tail)
        savefile(filename, html, utf8=True)

if __name__ == '__main__':
    target = (
        'http://comic.naver.com/webtoon/detail.nhn?titleId=697679&no=144&weekday=fri',
        '쌉니다 천리마마트'
    )
    NaverCrawl(*target).doit()