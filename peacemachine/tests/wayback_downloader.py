# get the proper domain format and requests the wayback snapshots
# make sure Ruby is installed + https://github.com/hartator/wayback-machine-downloader

import sys
import os
import re
import subprocess
import urllib.request
from urllib.error import URLError, HTTPError, ContentTooShortError
from tqdm import tqdm
import ast
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from newsplease import NewsPlease
from datetime import datetime
import random
from multiprocessing import Pool

if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p


def read_saved_urls():
    """
    function to read in all the saved urls
    """
    all_urls = []
    file_names = [fn for fn in os.listdir('data/wayback_urls/') if fn.endswith('_urls.txt')]
    for fn in file_names:
        with open(f'data/wayback_urls/{fn}', 'r', encoding='utf-8') as _file:
            all_urls.extend([url.strip() for url in _file.readlines()])
    return all_urls


class WaybackDownloader:

    def __init__(self, domain):
        self.domain = domain
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        # self.domain = self.get_domain_format(domain)
        self.exclude_regex = re.compile(r'(\/sports\/|\/deportes\/|\/meta\/|\/tags?\/|\/user\/)|\.(pdf|docx?|xlsx?|pptx?|epub|jpe?g|png|bmp|gif|tiff|webp|avi|mpe?g|mov|qt|webm|ogg|midi|mid|mp3|wav|zip|rar|exe|apk|css)$')
        self.exclude_regex_string = r'/(\/sports\/|\/deportes\/|\/meta\/|\/tags?\/|\/user\/)|\.(pdf|docx?|xlsx?|pptx?|epub|jpe?g|png|bmp|gif|tiff|webp|avi|mpe?g|mov|qt|webm|ogg|midi|mid|mp3|wav|zip|rar|exe|apk|css)$/'
        self.inserted_count = 0

    def get_domain_format(self, domain):
        """
        checks for proper url formatting (ex: include www. or not)
        """
        print(f'checking {domain}')
        try:
            req = urllib.request.Request(
                f'https://{domain}', 
                data=None, 
                headers={
                    'User-Agent': self.user_agent
                }
            )
            res = urllib.request.urlopen(req)
            return res.url
        except URLError or HTTPError:
            print('Error parsing domain :', domain)
            return(f'https://{domain}')

    def list_urls(self, write=True):
        """
        get the list of urls from the wayback machine
        """
        # pull the url list
        print('Pulling the url list')
        urls_string = subprocess.run(['wayback_machine_downloader', 
                        self.domain+'*', '-l'],
                        stdout=subprocess.PIPE, text=True).stdout
        # format the string output into a list                        
        urls_string = urls_string[urls_string.index('['):]
        urls_string = urls_string.replace('\n', '')
        self.domain_urls = [dd['file_url'] for dd in ast.literal_eval(urls_string)]
        # drop images and sports - should be done in wayback pull
        self.domain_urls = [dd for dd in self.domain_urls if not bool(self.exclude_regex.search(dd))]
        # filter out the urls I already have in the db
        print('Filtering out articles I already have')
        self.domain_urls = [url for url in tqdm(self.domain_urls) if not self.in_articles(url)]
        if write:
            with open(f'peacemachine/data/wayback_urls/{self.domain}_urls.txt', 'w') as _file:
                for url in self.domain_urls:
                    _file.write(f'{url}\n')

    def wb_download(self):
        """
        downloads the raw pages from the wayback machine
        """
        start_dir = os.getcwd()
        os.chdir('/media/devlab/HDD1/wayback')
        # os.system(f'wayback_machine_downloader {self.domain+"*"} -c 20 -x {self.exclude_regex_string}')
        subprocess.run(['wayback_machine_downloader', self.domain+'*', '-c', '20', '-x', self.exclude_regex_string])
        os.chdir(start_dir)

    def list_local_files(self):

    
    def process_local_files(self, file):
        """
        function to import a local html file from wayback
        :param file: string, full path ex: '/media/devlab/HDD1/wayback/websites/nytimes.com/
        :return: 
        """


    def in_articles(self, url): 
        """
        check to see if the url is already in the db
        """
        if bool(db.articles.find_one({'url': url})):
            return True
        return False


if __name__ == "__main__":
    # os.chdir('../..')
    _job = int(input('Enter 1 to get urls, enter 2 to only process urls, enter 3 to download direct from wayback (default is 1) ') or "1")
    if _job == 1:
        # get the urls
        file_names = [fn for fn in os.listdir('data/domains') if fn.startswith('domains_')]
        domains = []
        for fn in file_names:
            with open('data/domains/'+fn, 'r') as _file:
                domains.extend([dd.strip() for dd in _file.readlines()])
        for domain in tqdm(domains):
            if f'{domain}_urls.txt' not in os.listdir('data/wayback_urls/'):
                try:
                    wb = WaybackDownloader(domain)
                    print(f'Starting url retrival on {domain}')
                    wb.list_urls()
                except: # TODO add in exception type
                    print(f'ERROR ON: {domain}')


    elif _job == 2:
        # read in the urls
        all_urls = read_saved_urls()
        random.shuffle(all_urls)

        # process them in chunks of 1000
        url_chunks = [all_urls[i:i + 10000] for i in range(0, len(all_urls), 10000)]
        for chunk in tqdm(url_chunks):
            # download the pages
            pages = NewsPlease.from_urls(chunk)
            # convert to dictionaries
            pages = [v.__dict__ for k, v in pages.items() if v]
            # filter for publish date
            pages = [pg for pg in pages if pg['date_publish']]
            # filter for title
            pages = [pg for pg in pages if pg['title']]
            # insert the download method
            for pg in pages:
                pg['download_via'] = 'wayback'
            # insert
            try:
                db.articles.insert_many(pages, ordered=False)
            except BulkWriteError:
                print('BulkWriteError...')
            except TypeError:
                print('TypeError empty list...')

    elif _job == 3:
        # get the domains
        file_names = [fn for fn in os.listdir('data/domains') if fn.startswith('domains_')]
        domains = []
        for fn in file_names:
            with open('data/domains/'+fn, 'r') as _file:
                domains.extend([dd.strip() for dd in _file.readlines()])
        for domain in tqdm(domains):
            try:
                wb = WaybackDownloader(domain)
                wb.wb_download()
            except:
                print(f'Error on {domain}')


root = '/media/devlab/HDD1/wayback/websites/'

all_html = []

for path, subdirs, files in os.walk(root):
    for name in files:
        all_html.append( os.path.join(path, name) )


