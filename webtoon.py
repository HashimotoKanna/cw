import os
import re
import sys
import codecs
from multiprocessing import cpu_count, Pool
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlencode

whitespace_pattern = re.compile(r'\s+')


def urlencode_noquote(query): return urlencode(
    query, quote_via=lambda k, l, m, n: k)


def savefile(filepath, content):
    dir_path = os.path.dirname(filepath)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(filepath, 'wb') as f:
        f.write(content)


class MarumaruCrawl:
    ROOT = 'https://marumaru.town'
    INDEX_PAGE = ROOT + '/bbs/cmoic/'

    def __init__(self, comicId, name):
        self.name = name
        self.dir_path = os.path.join(os.path.dirname(__file__), self.name)
        self.comicId = comicId
        resp = requests.get(self.INDEX_PAGE + repr(self.comicId))
        soup = BeautifulSoup(resp.text, 'html.parser')
        self.comic_pages = {}
        for i, page in enumerate(soup.select('td.list-subject a')):
            sub_title = re.sub(whitespace_pattern, '', page.text)
            no = int(page['href'].split('/')[-1])
            self.comic_pages[no] = {
                'page': page['href'],
                'sub_title': sub_title
            }

    def crawl(self, start=float('-inf'), end=float('inf')):
        args = []
        for no, item in self.comic_pages.items():
            if no < start:
                break
            if no > end:
                continue
            args.append((
                self.comic_pages[no]['page'],
                self.comic_pages[no]['sub_title']))

        with Pool(processes=cpu_count()) as pool:
            pool.map(self._crawl_from_map, args)

    def _crawl_from_map(self, args):
        self._crawl(*args)

    def _crawl(self, page, sub_title):
        resp = requests.get(self.ROOT + page)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for i, img in enumerate(soup.select('div.view-img img')):
            img_data = requests.get(self.ROOT+img['src']).content
            subdir_path = os.path.join(self.dir_path, sub_title.zfill(3))
            img_filepath = os.path.join(subdir_path, repr(i).zfill(3)+'.jpg')
            savefile(img_filepath, img_data)
        print(self.name, sub_title, 'crawling complete')


class NaverCrawl:
    NAVER_WEBTOON_ROOT = 'https://comic.naver.com'
    NAVER_WEBTOON_DETAIL = NAVER_WEBTOON_ROOT + '/webtoon/detail.nhn?'
    NAVER_WEBTOON_LIST = NAVER_WEBTOON_ROOT + '/webtoon/list.nhn?'
    WEBTOON_PAGE_HTML_HEAD = '<html><head><title>'
    WEBTOON_PAGE_HTML_BODY = '''</title><style>
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
    WEBTOON_PAGE_HTML_TAIL = '</body></html>'
    WEBTOON_MAIN_HTML_BODY = '</title><style>*{background-color:black} body{text-align: center;}</style></head><body><h1>'

    no_pattern = re.compile(r'no=[0-9]+')

    def __init__(self, titleId):
        params = {
            'titleId': titleId
        }
        resp = requests.get(self.NAVER_WEBTOON_LIST +
                            urlencode_noquote(params))
        soup = BeautifulSoup(resp.text, 'html.parser')
        self.name = re.sub(whitespace_pattern, '',
                           soup.select('div.detail h2')[0].text)
        self.titleId = titleId
        self.latest = int(re.search(self.no_pattern, soup.select(
            'td.title a')[0]['href']).group(0)[3:])

    def crawl(self, start=1, end=None):
        if end is None:
            end = self.latest

        args = []
        dir_path = os.path.join(os.path.dirname(__file__), self.name)
        for no in range(start, end + 1):
            page_title = str(no)
            subdir_path = os.path.join(dir_path, page_title)
            html_file_path = os.path.join(subdir_path, page_title+'.html')
            if os.path.exists(html_file_path):
                print(html_file_path, 'is aleary exists')
                continue
            args.append((no, page_title, subdir_path, html_file_path))

        with Pool(processes=cpu_count()) as pool:
            pool.map(self._crawl_from_map, args)

        self.main_page(start, end, dir_path)

    def _webtoon_page_html(self, page_title, html_file_path, img_filepath_list):
        img_tags = ''.join(
            ['<img src="'+image_filename+'"/>' for image_filename in img_filepath_list])
        html = self.WEBTOON_PAGE_HTML_HEAD + page_title + self.WEBTOON_PAGE_HTML_BODY + \
            img_tags + '</div></div>' + self.WEBTOON_PAGE_HTML_TAIL
        with codecs.open(html_file_path, 'w', 'utf-8') as f:
            f.write(html)

    def _crawl_from_map(self, args):
        self._crawl(*args)

    def _crawl(self, no, page_title, subdir_path, html_file_path):
        params = {
            'titleId': self.titleId,
            'no': repr(no)
        }
        url = self.NAVER_WEBTOON_DETAIL + urlencode_noquote(params)
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        img_tags = soup.select('.wt_viewer img')

        img_filepath_list = []
        for i, img_tag in enumerate(img_tags):
            img_filepath = os.path.join(subdir_path, repr(i).zfill(3)+'.jpg')
            img_filepath_list.append(img_filepath)
            if os.path.exists(img_filepath):
                continue
            img_data = requests.get(img_tag['src'], headers={
                                    'Referer': url}).content
            savefile(img_filepath, img_data)

        self._webtoon_page_html(
            page_title, html_file_path, img_filepath_list)
        print(self.name, page_title, 'crawling complete')

    def main_page(self, start, end, dir_path):
        def atags(
            title): return '<a href="{name}/{name}.html">{name}</a><br>'.format(name=title)

        atags = ''.join(atags(repr(i))
                        for i in range(start, end + 1))
        html = self.WEBTOON_PAGE_HTML_HEAD + self.name + self.WEBTOON_MAIN_HTML_BODY + \
            self.name + '</h1>' + atags + self.WEBTOON_PAGE_HTML_TAIL

        index_html_filepath = os.path.join(dir_path, self.name + '.html')
        print(index_html_filepath)
        with codecs.open(index_html_filepath, 'w', 'utf-8') as f:
            f.write(html)
