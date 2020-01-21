# Naver webtoon/Youtube crawler 

just for fun

파이썬 공부를 시작했을 때 공부도 할 겸 재미도 볼 겸 만들어본 웹툰/유튜브 크롤러입니다. 

## requirements

`requests`

`bs4`

다음 명령어로 파이썬 패키지를 설치하세요. 

- Linux or Mac : `pip install requests bs4`

- Windows : `python -m pip install requests bs4`

## Usage 

원하는 웹툰을 크롤링 할 수 있도록 `main.py` 를 적절히 수정하세요. **신의탑** 을 크롤링 하고 싶다면 "**신의탑의 최신화 링크**"와 "**신의탑**"을 인자로 전달해야 합니다. 

```python
from webtoon import *

target = (
    'https://comic.naver.com/webtoon/detail.nhn?titleId=183559&no=461&weekday=mon',
    '신의탑'
)
nc = NaverCrawl(*target)
nc.doit()
```

그리고 `main.py` 를 실행하세요. 

`python main.py`

![cw](https://user-images.githubusercontent.com/16812446/72775222-dfeb2000-3c50-11ea-83ea-657bf210e3be.gif)

## View 

크롤링 된 이미지를 `.html` 파일로 재조립합니다. `html` 파일을 브라우저로 열어서 만화를 볼 수 있습니다. 

![html](https://user-images.githubusercontent.com/16812446/72775233-e7aac480-3c50-11ea-8ab1-e5da0e1064d1.PNG)
