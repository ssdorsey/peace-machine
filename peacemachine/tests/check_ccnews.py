# set up the workspace
from smart_open import open
from warcio.archiveiterator import ArchiveIterator
import pandas as pd
import urllib
from urllib.parse import urlparse
from urllib.request import urlretrieve
from tqdm import tqdm

def download(url):
  """
  Download and save a file locally.
  :param url: Where to download from
  :return: File path name of the downloaded file
  """
  url = 'https://commoncrawl.s3.amazonaws.com/' + url
  local_filename = urllib.parse.quote_plus(url)
  local_filepath = url.split('/')[-1]
  # download
  urlretrieve(url, local_filepath)
  return local_filepath

def pull_domain(url):
  domain = urlparse(url).netloc
  if domain.startswith('www.'):
    domain = domain[4:]
  return domain

def warc_domains(warc_path):
  urls = []
  warc_input = open(warc_path, 'rb')
  for record in tqdm(ArchiveIterator(warc_input)):
    if record.rec_type == 'response':
      if 'WARC-Target-URI' in record.rec_headers:
        url = record.rec_headers['WARC-Target-URI']
        urls.append(url)
  return urls

def warc_main(path):
  # download first
  local_path = download(path)
  warc_info = warc_domains(local_path)
  return warc_info


files =[
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701014014-00770.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701035412-00771.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701054520-00772.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701073022-00773.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701085523-00774.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701100844-00775.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701112420-00776.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701123940-00777.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701134959-00778.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701145423-00779.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701155602-00780.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701170121-00781.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701180534-00782.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701191541-00783.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701203600-00784.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701220326-00785.warc.gz',
        'crawl-data/CC-NEWS/2020/07/CC-NEWS-20200701234545-00786.warc.gz'
 ]

master_urls = []
for ff in tqdm(files):
  master_urls += warc_main(ff)

gaz = [url for url in master_urls if 'gazetatema.net' in url]
gaz