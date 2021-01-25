import re
from datetime import datetime

# scraping
from urllib.parse import urljoin, urlparse
import requests
# from selenium import webdriver

# processing text
import nltk

# DB queries 
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from newsplease import NewsPlease


def cut_dateline(text, thresh=30):
    """
    removes the dateline from the beginning of a news story
    :param text: string, generally the body of a news story that may have a 
                    dateline
    :param thresh: how far into the text to look for the dateline indicators
    :return: string with dateline cut out
    """
    if ' — ' in text[:30]:
        return text[text.index(' — ')+3:]
    elif '--' in text[:30]:
        return text[text.index('--')+2:]
    elif ' - ' in text[:30]:
        return text[text.index(' - ')+3:]
    # get rid of the CNN dateline
    elif '(CNN)' in text[:30]:
        return text[text.index('(CNN)')+5:]
    elif ': ' in text[:20]:
        return text[text.index(': ')+2:]
    elif '\n' in text[:20]:
        return text[text.index('\n')+1:]
    # if no dateline is found, return the same string
    return text


def cut_url_query(url):
    """
    cuts any query off the supplied url
    """
    return urljoin(url, urlparse(url).path) 


def build_combined(doc):
    """
    combines titles and text of docs as they are available
    :param doc: dictionary from news-please output
    :return: string of combined text
    """
    try:
        if doc['title'] and doc['maintext']:
            return doc['title'] + '. ' + nltk.sent_tokenize(cut_dateline(doc['maintext']))[0] # TODO: multilingual tokenizer needed
        elif doc['title'] and doc['description']:
            return doc['title'] + '. ' + nltk.sent_tokenize(cut_dateline(doc['description']))[0]
    except:
        pass

    return doc['title']


def pull_source_domain(url):
    """
    Pull the domain (without www.) from a url
    :param: string in url format
    :return: string of only domain
    """
    domain = urlparse(url).netloc
    if domain.startswith('www.') or domain.startswith('ww2.'):
        domain = domain[4:]
    return domain


def regex_from_list(_list, compile=True):
    """
    Creates a regex from a list of patterns
    :param _list: list of patterns
    :param compile: True if return compiled regex, False if return string
    :return: compiled regex
    """
    if compile:
        return re.compile('(' + '|'.join(_list) + ')')
    else: 
        return '(' + '|'.join(_list) + ')'


# TODO: convert this to use the native download_crawler in newsplease
def download_url(uri, url, download_via=None, insert=True, overwrite=False):
    """
    process and insert a single url
    """
    db = MongoClient(uri).ml4p

    try:
        # download
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        }
        response = requests.get(url, headers=header)
        # process
        article = NewsPlease.from_html(response.text, url=url).__dict__
        # add on some extras
        article['date_download']=datetime.now()
        if download_via:
            article['download_via'] = download_via
        # insert into the db
        if not insert:
            return article
        if article:
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f"articles-{year}-{month}"
            except:
                colname = 'nodate'
            try:
                if overwrite:
                    db[colname].replace_one(
                        {'url': url},
                        article,
                        upsert=True
                    )
                    db['urls'].insert_one({'url': article['url']})
                else:
                    db[colname].insert_one(
                        article
                    )
                    db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                pass
        return article
    except: # TODO detail exceptions
        pass



class urlFilter:
    """
    class for filtering urls
    """
    def __init__(self, uri, source_collection='sources'):
        self.db = MongoClient(uri).ml4p
        self.sources = {
            doc.get('source_domain'): doc for doc in self.db[source_collection].find()
        }

    def filter_url(self, url):
        """
        :param url: string version of url to check
        :return: boolean for whether to use the url or not
        """
        # first get the source info
        _source_domain = pull_source_domain(url)
        source_info = self.sources.get(_source_domain)

        if not source_info:
            return False
        
        # start by checking the blacklist
        if source_info.get('blacklist_url_patterns'):
            if any([pat in url for pat in source_info['blacklist_url_patterns']]):
                return False

        # then check the whitelist
        if source_info.get('whitelist_url_patterns'):
            if any([pat in url for pat in source_info['whitelist_url_patterns']]):
                return True
            else:
                return False

        # if none of the filters hit it, keep the url
        return True

    def filter_list(self, list_urls):
        """
        :param list_urls: list of urls to filter
        """
        return [uu for uu in list_urls if self.filter_url(uu)]


# class htmlFilter:
#     """
#     class for filtering html
#     TODO: convert this to regex
#     """
#     def __init__(self, uri, source_collection='sources'):
#         self.db = MongoClient(uri).ml4p
#         self.sources = {
#             doc.get('source_domain'): doc for doc in self.db[source_collection].find()
#         }

#     def filter_html(self, url, html):
#         """
#         :param url: string version of url to check
#         :return: boolean for whether to use the url or not
#         """
#         # first get the source info
#         _source_domain = pull_source_domain(url)
#         source_info = self.sources.get(_source_domain)

#         if not source_info:
#             return False
        
#         # start by checking the blacklist
#         if source_info.get('blacklist_url_patterns'):
#             if any([pat in url for pat in source_info['blacklist_html_patterns']]):
#                 return False

#         # then check the whitelist
#         if source_info.get('whitelist_url_patterns'):
#             if any([pat in url for pat in source_info['whitelist_html_patterns']]):
#                 return True
#             else:
#                 return False

#         # if none of the filters hit it, keep the url
#         return True

#     def filter_list(self, list_urls):
#         """
#         :param list_urls: list of urls to filter
#         """
#         return [uu for uu in list_urls if self.filter_html(uu)]
