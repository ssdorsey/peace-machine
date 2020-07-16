"""
Script for downloading the mass of urls I pull from GDELT
"""

import os
# from tqdm import tqdm
from p_tqdm import p_umap
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
from pymongo import MongoClient
from multiprocessing import Pool
from newsplease import NewsPlease
from datetime import datetime


def process_url(url):
    """
    process and insert a single url
    """
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
        article['download_via'] = 'gdelt'
        # insert into the db
        if os.getlogin() == 'Batan':
            db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
        if os.getlogin() == 'devlab':
            db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p
        else:
            db = MongoClient('mongodb://ml4pAdmin:ml4peace@vpn.ssdorsey.com').ml4p
        db.articles.insert_one(article)
    except: # TODO detail exceptions
        pass

if __name__ == '__main__':
    # read in file list
    folds = pd.read_csv('DELETE_gdelt_url_folds.csv')
    fold = int(input('Which fold? [1, 15]'))
    files = list(folds[folds['fold']==fold]['file'])
    for csv in files:
        # load the data
        urls = list(pd.read_csv(f'data/GDELT_urls/urls/{csv}').iloc[:, 0])
        p_umap(process_url, urls)
        # os.rename(f'data/GDELT_urls/urls/{csv}', f'data/GDELT_urls/urls/done/{csv}')





