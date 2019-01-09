
# coding:utf-8

import os, codecs, requests, re, time
from urllib.parse import quote_plus as urlencode
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip

START_TIME = time.time()

ROOT_youtube = 'https://www.youtube.com'
ROOT_download = 'https://qdownloader.net/download?video='
ROOT_subtitle = 'https://downsub.com'
INCLUDED_B_A_TAG_SIZE = 1000

get_var = lambda url: urlencode(url.split('v=')[1])
get_var_encoded = lambda url: url.split('v%3D')[1]
get_html = lambda url: requests.get(url).text
get_soup = lambda html: BeautifulSoup(html, 'html.parser')

def get_video_list(keyword):
    f = codecs.open(keyword+'_channel.txt', 'r', 'utf-8')
    html = ''
    for x in f:
        html += x
    else:
        f.close()

    soup = get_soup(html)
    video_titles = soup.select('a#video-title')

    video_list = []
    for video_title in video_titles:
        video_link = ROOT_youtube + video_title['href']
        # print(video_link)
        video_list.append(video_link)
    
    return video_list

def get_date(video_url):
    html = get_html(video_url)
    date_index = html.find('게시일')

    if date_index != -1:
        date = html[date_index + 5: date_index + 19].split('.')
        date = date[0] + date[1] + date[2]
        return date
    else:
        # 실시간 스트리밍 전체 영상인 경우
        return False

# def get_audio(video_url, directory='output', remove_mp4=True):
def get_audio(video_filepath):
    # video_filepath = get_video(video_url)[1]
    if not os.path.exists(video_filepath):
        return False
    audio_filepath = '.'.join((video_filepath.rsplit('.', maxsplit=1)[0], 'mp3'))
    # subtitle_filepath = '.'.join((video_filepath.rsplit('.', maxsplit=1)[0], 'txt'))
    if os.path.exists(audio_filepath):
        print('[-]', 'File already exists =>', audio_filepath)
    else:
        try:
            clip = VideoFileClip(video_filepath)
        except OSError:
            print('[-]', 'unknown error in VideoFileClip module')
            return False
        else:
            clip.audio.write_audiofile(audio_filepath)
            return True
        
    # if os.path.exists(subtitle_filepath):
    #     print('[-]', 'File already exists =>', audio_filepath)
    # else:
    #     print('[+]', 'Crawl n Parse subtitle =>', subtitle_filepath)
    #     get_subtitle(video_url, subtitle_filepath)


def get_video(video_url, directory='output', manifest_content=[]):
    """\
    video_url : 유투브의 동영상 URL. 예를 들어 'https://www.youtube.com/watch?v=jqi8p2r-iYU'
    directory : 동영상이 크롤링되어 저장될 디렉토리
    manifest_content : 동영상이 이미 크롤링되어있을 경우 크롤링을 하지 않기 위한 동영상 목록임.
    """
    url = ROOT_download + urlencode(video_url)
    var = get_var_encoded(url)
    if var in manifest_content:
        print('[-]', var, 'is in manifest.. pass this video')
        return False
    soup = get_soup(get_html(url))

    try:
        title = soup.select('span.title')[0].text
    except IndexError:
        print('[-]', 'This video url is not valid or is private')
        return False, None
    else:
        title = title.replace('?', '').replace('^', '').replace('*', '').replace('|', '').replace('/', '').replace('\\', '').replace('>','').replace('<','').replace(':','').replace('"','')

        date = get_date(video_url)
        if date:
            filepath = os.path.join(directory, date+' '+title+'.mp4')
            if not os.path.exists(directory):
                os.mkdir(directory)
            if os.path.exists(filepath):
                print('[-]', 'File already exists =>', filepath)
                return False, filepath
            else:
                print('[+]', 'Crawl =>', filepath)
                with open(filepath, 'wb') as f:
                    video_list = soup.select('td a')
                    r = requests.get(video_list[0]['href'], stream=True)
                    for chunk in r.iter_content(chunk_size = 1024*100):
                        f.write(chunk)
                return True, filepath
        else:
            # 실시간 스트리밍 전체 영상인 경우
            print('[-]', 'This video is entire streaming video =>', title)
            return False, None

def test():
    keyword, directory = 'src/gulza', '글자'
    keyword, directory = 'src/kst', '킴성태'
    keyword, directory = 'src/usn', '유소나'
    
    if not os.path.exists(directory):
        os.mkdir(directory)
        
    manifest_path = os.path.join(directory, 'manifest.txt')
    manifest = open(manifest_path, 'a')
    with open(manifest_path, 'r') as f:
        manifest_content = f.read().split()

    video_list = get_video_list(keyword)
    for video in video_list:
        if get_video(video, directory, manifest_content)[0]:
            manifest.write(get_var(video)+'\n')

def get_subtitle(video_url, subtitle_filepath):
    subtitle_url = ROOT_subtitle + '/?url=' + urlencode(video_url)
    html = get_html(subtitle_url)
    eng_idx = html.find('English')
    INCLUDED_B_A_TAG_TEXT = html[eng_idx-1000:eng_idx]
    soup = get_soup(INCLUDED_B_A_TAG_TEXT)
    try:
        target = soup.select('b a')[-1]['href'][1:]
    except IndexError:
        print('[-]', 'This video does not has subtitle')
    else:
        subtitle = get_html(ROOT_subtitle+target).split('\n\n')
        for i, v in enumerate(subtitle):
            subtitle[i] = ' '.join(re.split(r'<\s*\/\s*\w\s*.*?>|<\s*br\s*>|<\s*\w.*?>', v.split('\n')[-1]))
        subtitle = '\n'.join(subtitle)
        with open(subtitle_filepath, 'w') as f:
                f.write(subtitle)

if __name__ == '__main__':
    # import sys
    # from optparse import OptionParser

    # parser = OptionParser()
    # parser.add_option("-a", "--audio", default=False, action="store_true", help="extract audio from youtube")
    # parser.add_option("-v", "--video", default=False, action="store_true", help="extract full videofrom youtube")

    # options, args = parser.parse_args()
    # if args:
    #     if options.video:
    #         if options.audio:
    #             get_audio(args[0], remove_mp4=False)
    #         else:
    #             get_video(args[0])
    #     else:
    #         if options.audio:
    #             get_audio(args[0])

    urls = [
        'https://www.youtube.com/watch?v=QdfcrCxQFfU',
        'https://www.youtube.com/watch?v=QFJiCe5bc20',
        'https://www.youtube.com/watch?v=A-Fo_W_9tz4',
        'https://www.youtube.com/watch?v=qr6HBLlVWiE',
        'https://www.youtube.com/watch?v=AWxLDwLcUlk',
        'https://www.youtube.com/watch?v=PKZCXSEZaTA',
        'https://www.youtube.com/watch?v=vsjjiK2qUQY',
        'https://www.youtube.com/watch?v=AcX4db0NFwE',
        'https://www.youtube.com/watch?v=4N60Ae_VcDU',
        'https://www.youtube.com/watch?v=rSPpt8ymcvQ',
        'https://www.youtube.com/watch?v=u7AWqmEeaJk',
        'https://www.youtube.com/watch?v=8AKxbpR_cdo',
        'https://www.youtube.com/watch?v=_YN-6JSw4B8',
        'https://www.youtube.com/watch?v=-t6pnUUk1No',
        'https://www.youtube.com/watch?v=TbGr6EjjNSM',
        'https://www.youtube.com/watch?v=hG1gbOjWWdI',
        'https://www.youtube.com/watch?v=uBzUfjkdPq4',
        'https://www.youtube.com/watch?v=Acv8deK5Rok',
        'https://www.youtube.com/watch?v=hkt-AWerpU8',
        'https://www.youtube.com/watch?v=i5cQirTYXQk',
        'https://www.youtube.com/watch?v=zucBfXpCA6s',
        'https://www.youtube.com/watch?v=4R0mOGqYnL8',
        'https://www.youtube.com/watch?v=Wpeuy6YmyP0',
        'https://www.youtube.com/watch?v=FHO3wtNYmOI',
        'https://www.youtube.com/watch?v=TrH1jSHVk4c',
        'https://www.youtube.com/watch?v=xTI5BhG-vEE',
        'https://www.youtube.com/watch?v=3FuhNCqO-K8',
        'https://www.youtube.com/watch?v=x_WCqb7R4tw',
        'https://www.youtube.com/watch?v=PV_8ZESIqpo',
        'https://www.youtube.com/watch?v=TbGr6EjjNSM',
        'https://www.youtube.com/watch?v=X-jdl9hcCeg'
    ]

    import os
    files = os.listdir(os.getcwd())

    from multiprocessing import Pool, cpu_count

    p = Pool(cpu_count())
    
    videos = []
    
    # for video in set(files):
        # video_filepath = get_video(url)
        # if video.endswith('mp4'):
            # get_audio(video)

    for file in files:
        if file.endswith('mp4'):
            videos.append(file)

    print(p.map(get_audio, videos))
    print("EXECUTION TIME : ", START_TIME - time.time())
