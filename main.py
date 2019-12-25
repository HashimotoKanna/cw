from webtoon import *

target = (
    'https://comic.naver.com/webtoon/detail.nhn?titleId=183559&no=461&weekday=mon',
    '신의탑'
)
nc = NaverCrawl(*target)
nc.doit()