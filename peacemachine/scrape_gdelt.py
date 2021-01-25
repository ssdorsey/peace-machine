"""
Script for collecting URLS that GDLET has and I don't 
"""
import getpass
from p_tqdm import p_umap
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pymongo import MongoClient
from functools import partial

from peacemachine.helpers import download_url
from peacemachine.helpers import urlFilter

if getpass.getuser() == 'spenc':
    _uri = 'mongodb://ml4pAdmin:ml4peace@192.168.176.240'
else:
    _uri = 'mongodb://ml4pAdmin:ml4peace@vpn.ssdorsey.com'

db = MongoClient(_uri).ml4p
_source_domains = db.sources.distinct('source_domain')

n_cpu = 8

def check_domains(gdelt_url):
    """
    :param gdelt_url: the url to the gdelt file to check
    """
    # check to see if I have never processed this link
    __db = MongoClient(_uri).ml4p
    if __db.gdelt.count_documents({'url': gdelt_url}, limit=1) == 0:
        return _source_domains

    # if already run, see if needs rerun for new domains
    old_source_domains = __db.gdelt.find_one({'url': gdelt_url})['included_domains']

    # compare to the current domains
    missing = list(set(_source_domains) - set(old_source_domains))

    if len(missing) > 0:
        return missing

    # if I don't need to run this link
    return False


def parse_file(gdelt_url):

    try:
        _db = MongoClient(_uri).ml4p

        # first check if I need to download / get the domains
        missing_domains = check_domains(gdelt_url)

        if not missing_domains:
            return

        # if I need to get it
        # load into memory
        df = pd.read_table(gdelt_url, compression='zip', header=None)
        urls = df.iloc[:, -1]

        # filter urls for my domains
        # TODO: figure out how much more efficient it is to just check the domains from missing_domains

        # check that I don't already have them in the db
        urls = pd.Series([url for url in urls if _db.urls.count_documents({'url': url}, limit=1) == 0])

        # check that I don't have any of the blacklist patterns
        ufilter = urlFilter(_uri)
        urls = ufilter.filter_list(urls)

        # download the urls
        for url in urls:
            download_url(url, _uri, download_via='gdelt')

        # update the entry
        _db.gdelt.update_one(
            {
                'url': gdelt_url
            },
            {
                '$set': {
                    'included_domains': _source_domains
                }
            },
            upsert=True
        )
    except:
        print('PARSING ERROR')

def gdelt_download(uri, n_cpu=0.5):
    pass

# TODO: get this working as a function call

if __name__ == "__main__":
    # uri = 'mongodb://ml4pAdmin:ml4peace@192.168.176.240'
    # db = MongoClient(uri).ml4p
    # source_domains = db.sources.distinct('source_domain')

    # global _uri
    # _uri = uri
    # global _source_domains
    # _source_domains = source_domains

    # get all the v1 links http://data.gdeltproject.org/events/index.html
    v1_index = BeautifulSoup(requests.get(
        'http://data.gdeltproject.org/events/index.html').content)

    v1 = [ff['href'] for ff in v1_index.find_all('a')]
    v1 = ['http://data.gdeltproject.org/events/'+ff for ff in v1 if ff.endswith('.zip') and
            not ff.startswith('GDELT.MASTERREDUCED')]

    # get the v2 english links
    v2_eng_index = requests.get('http://data.gdeltproject.org/gdeltv2/masterfilelist.txt').text.split('\n')
    v2_eng = [ll.split() for ll in v2_eng_index]
    v2_eng = [ll for sublist in v2_eng for ll in sublist if ll.endswith('.export.CSV.zip')]

    # get the v2 trans links
    v2_trans_index = requests.get('http://data.gdeltproject.org/gdeltv2/masterfilelist-translation.txt').text.split('\n')
    v2_trans = [ll.split() for ll in v2_trans_index]
    v2_trans = [ll for sublist in v2_trans for ll in sublist if ll.endswith('.export.CSV.zip')]

    # combine them
    files = list(set(v1+v2_eng+v2_trans))

    # sort by most recent
    files = sorted(files, key = lambda x: int(x.split('/')[4][:x.split('/')[4].index('.')]), reverse=True)

    p_umap(parse_file, files, num_cpus=n_cpu)

    # checking for gazetatema
    # files = v2_trans
    # # files = [ff for ff in files if '202007' in ff or '202008' in ff]
    # files = [ff for ff in files if '202007' in ff]

    # all_gaz = []

    # from tqdm import tqdm
    # for ff in tqdm(files):
    #     try:
    #         df = pd.read_table(ff, compression='zip', header=None)
    #         urls = df.iloc[:, -1]
    #         urls = urls[urls.str.contains('gazetatema.net')]
    #         all_gaz += list(urls)
    #     except:
    #         print('PROBLEM ON: ' + ff)
    
    # # p_umap(partial(download_url, uri='mongodb://ml4pAdmin:ml4peace@192.168.176.240', overwrite=True), all_gaz)

    # for ll in tqdm(all_gaz):
    #     download_url(uri='mongodb://ml4pAdmin:ml4peace@192.168.176.240', url=ll, overwrite=True)
