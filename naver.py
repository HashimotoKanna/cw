# -*- coding: utf-8 -*-

from crawlbase import *

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

    def doit(self):
        for no in range(1, self.latest + 1):
            self.crawl(self.titleId, no)
        else:
            self.indexing()

    def crawl(self, titleId, no):
        url = join( self.ROOT, '?', 'titleId=', titleId, '&no=', str(no) )
        soup = getsoup(url)

        title = soup.select('.comicinfo h2')[0].text.split()[0]
        subtitle = str(no)+'화'

        dir = makedir(title, subtitle)
        
        imgs = soup.select('.wt_viewer img')

        for i, tag in enumerate(imgs):
            filename = getpath(dir, repr(i+1)+'.jpg')

            jpg = get(tag['src'], headers = {'Referer' : url}).content
            savefile(filename, jpg)

        self.htmling(subtitle, len(imgs), dir)
        msg = ' '.join((title, subtitle, '크롤링 완료'))
        print(msg)

    def indexing(self):
        getatag = lambda NAME: '<a href="{name}/{name}.html">{name}</a><br>'.format(name=NAME)
        
        head = '<html><head><title>'+self.name+'</title><style>*{background-color:black} body{text-align: center;}</style></head>'
        '<body><h1>'+self.name+'</h1>'
        tail = '</body></html>'
        atags = join( getatag(idx)+'\n' for idx in self.index )

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
