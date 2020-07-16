"""
Script for collecting URLS that GDLET has and I don't 
"""
import sys
import os
from p_tqdm import p_umap
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import pandas as pd
import io
from pymongo import MongoClient
from multiprocessing import Pool


def parse_file(url):
    try:
        # load domains I'm interested in
        available_countries = [fn.split('_')[1].split('.')[0] for fn in os.listdir('D:/Dropbox/peace-machine/peacemachine/data/domains')
                            if fn.startswith('domains_')]

        domains = []
        for ac in available_countries:
            with open(f'D:/Dropbox/peace-machine/peacemachine/data/domains/domains_{ac}.txt', 'r') as _f:
                domains.extend([dd.strip() for dd in _f.readlines()])
        domains = [dd.replace('.', '\.') for dd in domains]
        domains = '|'.join(domains)

        # download
        _file = url.split('/')[-1]
        s=requests.get(url).content
        open(f'D:/temp/{_file}', 'wb').write(s)
        # load into memory
        df = pd.read_table(f'D:/temp/{_file}', compression='zip', header=None)
        urls = df.iloc[:, -1]
        # filter urls for my domains
        urls = urls[urls.str.contains(domains)]
        # check that I don't already have them in the db
        if sys.platform=='win32' or os.environ['USER'] != 'devlab':
            db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
        else:
            db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p
        urls = pd.Series([url for url in urls if not bool(db.articles.find_one({'url': url}))])
        # delete file
        os.remove(f'D:/temp/{_file}')
        # write urls to disk
        urls.to_csv(f'D:/temp/urls/{url.split("/")[-2]+"_"+_file[:-4]}'.lower(), index=False)
    except:
        print('Connection error: ', url)

if __name__ == '__main__':

    # get all the v1 links http://data.gdeltproject.org/events/index.html
    # v1_index = BeautifulSoup(requests.get(
    #     'http://data.gdeltproject.org/events/index.html').content)

    # v1 = [ff['href'] for ff in v1_index.find_all('a')]
    # v1 = ['http://data.gdeltproject.org/events/'+ff for ff in v1 if ff.endswith('.zip') and
    #         not ff.startswith('GDELT.MASTERREDUCED')]

    # get the v2 english links
    v2_eng_index = requests.get('http://data.gdeltproject.org/gdeltv2/masterfilelist.txt').text.split('\n')
    v2_eng = [ll.split() for ll in v2_eng_index]
    v2_eng = [ll for sublist in v2_eng for ll in sublist if ll.endswith('.export.CSV.zip')]

    # get the v2 trans links
    v2_trans_index = requests.get('http://data.gdeltproject.org/gdeltv2/masterfilelist-translation.txt').text.split('\n')
    v2_trans = [ll.split() for ll in v2_trans_index]
    v2_trans = [ll for sublist in v2_trans for ll in sublist if ll.endswith('.export.CSV.zip')]

    # combine them
    # files = list(set(v1+v2_eng+v2_trans))
    files = list(set(v2_eng+v2_trans))
    _done = set(os.listdir('D:/temp/urls/'))
    files = [ff for ff in files if (ff.split("/")[-2]+"_"+ff.split("/")[-1][:-4]).lower() not in _done]

    # all_urls = []
    # for ff in tqdm(files):
        # parse_file(ff)
    p_umap(parse_file, files, num_cpus=30)

