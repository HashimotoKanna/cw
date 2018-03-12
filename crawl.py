# coding: utf-8

from multiprocessing import Process
import threading

from naver import NaverCrawl
from marumaru import MarumaruCrawl

'''블리치, 나루토, 데스노트, 
배틀짱, 코난, 고르고13, 김전일
더파이팅 테니스의왕자 헬싱 원펀맨 '''

ninfo = (
    'http://comic.naver.com/webtoon/detail.nhn?titleId=602910&no=206&weekday=mon',
    '윈드브레이커'
)
dragon = (
    'http://comic.naver.com/webtoon/detail.nhn?titleId=568986&no=138&weekday=sat',
    '용이산다'

)
love = (
'http://comic.naver.com/webtoon/detail.nhn?titleId=570503&no=214&weekday=thu',
'연애혁명'
)
minfo = (
    'http://marumaru.in/?c=1/30&cat=%EC%9B%94%EA%B0%84&sort=subject&mod=view&uid=82810',
    '진격의 거인'
)
god = (
'http://comic.naver.com/webtoon/detail.nhn?titleId=697685&no=78&weekday=thu',
'신과함께'
)
tennise = (
'http://marumaru.in/b/manga/140769',
'테니스의 왕자'
)
collage= (
'http://comic.naver.com/webtoon/detail.nhn?titleId=679519&no=187&weekday=thu',
'대학일기'
)
# NaverCrawl(*ninfo).doit()
# NaverCrawl(*dragon).doit()
# NaverCrawl(*love).doit()
NaverCrawl(*collage).doit()
# MarumaruCrawl(*minfo).doit()
# MarumaruCrawl(*tennise).doit()