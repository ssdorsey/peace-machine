import os
from p_tqdm import p_umap
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
from pymongo import MongoClient
from newsplease import NewsPlease
from datetime import datetime
import sklearn

def keep_url(url):
    if db.articles.find({'url': url}).limit(1).count() > 0:
        return True
    return True

def process_url(url, download_via=None):
    """
    process and insert a single url
    """
    # make sure I don't already have it
    # db = MongoClient('mongodb://ml4pAdmin:ml4peace@10.142.15.205').ml4p
    # if os.getlogin() != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
    # else:
    #     db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p
    if db.articles.find({'url': url}).count() > 0: 
        return
    try:
        # download
        header = {
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36'
            '(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')
        }
        response = requests.get(url, headers=header).text
        # process
        article = NewsPlease.from_html(response, url=url).__dict__
        # add on some extras
        article['date_download']=datetime.now()
        if download_via:
            article['download_via'] = download_via
        # insert into the db
        db.articles.insert_one(
            article
        )
    except: # TODO detail exceptions
        pass

if __name__ == '__main__':
    # read in file list
    fold = int(input('What fold? [1-15]'))
    all_urls = pd.read_csv('all_urls.csv')
    all_urls = all_urls[all_urls['fold']==fold]
    all_urls = all_urls.drop('fold', axis=1)
    # shuffle
    all_urls = sklearn.utils.shuffle(all_urls)
    urls = list(all_urls['url'])
    download_vias = list(all_urls['download_via'])
    p_umap(process_url, urls, download_vias, num_cpus=50)





