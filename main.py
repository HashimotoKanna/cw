from webtoon import *

def test_GOD_TOP():
    nc = NaverCrawl(183559) # 신의탑
    nc.crawl(442)

def test_OnePiece():
    mc = MarumaruCrawl(19967, 'onepiece') # 원피스 
    mc.crawl(49134)

# https://marumaru.town/bbs/cmoic/19967/49134
if __name__ == '__main__':
    test_OnePiece()
