import requests
import json
from datetime import datetime
from multiprocessing import Pool, Queue, Process, current_process, Lock
import os
from glob import glob
from bs4 import BeautifulSoup
import re
import time
import sys
import urllib2

def set_encode(encode='utf-8'):
    import sys
    reload(sys)
    sys.setdefaultencoding(encode)
    return


def parse_search_result(folder, imdb_id):
    # print imdb_id
    html_file = folder + imdb_id + '/search_result.html'
    result_list = []
    if not os.path.isfile(html_file):
        print imdb_id, 'no html file'
    else:
        with open(html_file, 'r') as f:
            page_soup = BeautifulSoup(f.read(), 'lxml')
        try:
            # labels1 = page_soup.find_all('span', class_='label label-success')
            labels = page_soup.find_all('span', class_='label')
            langs = page_soup.find_all('span', class_='sub-lang')
            downloads = page_soup.find_all('a', class_='subtitle-download')
            if len(labels) != len(langs) or len(labels) != len(downloads):
                print imdb_id
                print len(labels), len(langs), len(downloads)
            for label, lang, download in zip(labels, langs, downloads):
                if lang.get_text() == 'English' or lang.get_text() == 'Chinese':
                    r = requests.get('http://www.yifysubtitles.com/'+download['href'])
                    sub_soup = BeautifulSoup(r.text, 'lxml')
                    subtitle_url = get_subtitle_url(sub_soup)
                    result = {
                        'label': label.get_text(),
                        'language': lang.get_text(),
                        'download': download['href'],
                        'subtitle': subtitle_url
                    }
                    result_list.append(result)
                    # print label.get_text(), lang.get_text(), download['href'], subtitle_url
        except Exception as e:
            print e
    return imdb_id, result_list


def get_subtitle_url(page_soup):
    url = None
    try:
        a = page_soup.find('a', class_='btn-icon download-subtitle')
        url = a['href']
    except Exception as e:
        print e
    return url


def download_subtitle(folder, imdb_id):
    json_file = folder + 'info/' + imdb_id + '.json'
    flag = False
    if os.path.isfile(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
        for result in data['results']:
            if result['language'] == 'English':
                save_file = folder + 'subtitle/' + imdb_id + '.zip'
                try:
                    url = result['subtitle']
                    f = urllib2.urlopen(url)
                    with open(save_file, "wb") as code:
                        code.write(f.read())
                    flag = True
                    break
                except Exception as e:
                    print imdb_id, e
    return flag


def callback(rst):
    global proc_start_time
    global counter
    global with_subtitle
    # save result
    # id = rst[0]
    # result = {'id': id, 'number': len(rst[1]), 'results': rst[1]}
    # with open('/media/Data2/YIFY/info/'+id+'.json', 'w') as f:
    #     f.write(json.dumps(result, indent=2))
    if rst:
        with_subtitle += 1
    counter = counter + 1
    cnt = counter
    if cnt % 1000 == 0:
        cur_time = time.time()
        print '{} movies finished, speed {} movies/sec'.format(cnt, cnt/(cur_time - proc_start_time))
        sys.stdout.flush()


def count_results(folder, imdb_id):
    json_file = folder + 'info/' + imdb_id + '.json'
    if os.path.isfile(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
    return len(data['results'])


if __name__ == '__main__':
    set_encode()
    folder = '/media/Data2/'
    movie_list_file = folder+'movie_dataset/movie_list.txt'
    with open(movie_list_file, 'r') as f:
        lines = f.readlines()
    imdb_id_list = [x.split(',')[0].strip() for x in lines]
    tmdb_id_list = [x.split(',')[1].strip() for x in lines]
    print len(imdb_id_list), 'movies.'

    # imdb_id_list = ['tt0111161']
    # imdb_id_list = imdb_id_list[:1000]

    print datetime.now(), 'downloading...'
    global proc_start_time
    global counter
    global with_subtitle
    with_subtitle = 0
    counter = 0
    proc_start_time = time.time()
    pool = Pool(8)
    jobs = [
        pool.apply_async(
            download_subtitle,
            args=(folder+'YIFY/', x),
            callback=callback)
        for x in imdb_id_list]
    pool.close()
    pool.join()

    print with_subtitle, 'movies have subtitle.'
