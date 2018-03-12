# -*- coding: utf8 -*-

from crawlbase import *

class MarumaruCrawl(CrawlBase):
    ROOT = 'http://wasabisyrup.com'

    def __init__(self, target, name):
        soup = getsoup(target)
        indexes = soup.select('#vContent a')

        self.index = [
            idx for idx in indexes \
            if idx.text.find(name) == 0
        ]

    def doit(self):
        for idx in self.index:
            self.crawl(idx)

    def crawl(self, url_target):
        url = url_target['href']
        soup = getsoup(url)

        titles = soup.select('.title-text span')
        title = titles[0].text
        subtitle = titles[1].text

        dir = makedir(title, subtitle)

        imgs = soup.select('.article-gallery img')

        for i, img in enumerate(imgs):
            if i < 10:
                filename = getpath(dir, '00'+repr(i)+'.jpeg')
            elif 10 <= i < 100:
                filename = getpath(dir, '0'+repr(i)+'.jpeg')
            else:
                filename = getpath(dir, repr(i)+'.jpeg')

            jpeg = get(self.ROOT+img['data-src']).content
            savefile(filename, jpeg)
            
            percentage = round(i / len(imgs) * 100)
            msg = ' '.join((
                    title, subtitle, '크롤링 중..', repr(percentage), '%'
            ))
            print(msg)
