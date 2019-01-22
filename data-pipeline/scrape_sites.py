""""
backup of collect_international
"""
import urllib.request # what we use to download html into python
import gzip # for opening compressed files (.gz)
from bs4 import BeautifulSoup # for parsing the html once we download
from time import sleep # for pausing the script so we don't overload servers
from tqdm import tqdm # useful little package for creating progress bars
from datetime import datetime, timedelta, date # for managing date formats
import re


# ------------------------------------------------------------------------------
# functions
# ------------------------------------------------------------------------------
def read_sitemap(site_url, compressed=False):
    """
    Pulls all the links from a .xml url

    Keyword arguments:
    site_url -- the address of the .xml file
    compressed -- if the address is a .xml.gz
    """
    # call the website
    response = urllib.request.urlopen(site_url)
    # open with gzip if it's compressed
    if compressed:
        gunzip_response = gzip.GzipFile(fileobj=response)
        content = gunzip_response.read()
        c_d = content.decode('utf-8')
    else:
        c_d = response.read()
    # parse in BeautifulSoup
    re_soup = BeautifulSoup(c_d, 'lxml')
    # pull out all the urls
    urls = [loc.string for loc in re_soup.find_all('loc')]
    # sleep for a second so as to not accidentally DDoS
    # sleep(1)
    return urls


def nyt_gen(year, month):
    """
    creates date-formatted links to the NYT sitemaps
    """
    # checks for a 2-digit month format, ex: '02'
    if not type(month) is str:
        month = str(month)
        if len(month) < 2:
            month = '0' + month
    return f'https://www.nytimes.com/sitemaps/www.nytimes.com/sitemap_{year}_{month}.xml.gz'


def collect_nyt():
    """
    main function to collect all the nyt links
    """
    # all the years we want from the NYT
    years = range(2000, 2019)
    # all the months we want from the NYT
    months = range(1, 13)
    # create a list of all the sitemap urls
    nyt_sitemaps = [nyt_gen(year, month) for year in years for month in months]
    # loop through every sitemap and get the links
    for sm in tqdm(nyt_sitemaps): # tqdm just gives us an easy progress tracker
        links = read_sitemap(sm)
        # save the links to a text file
        with open('links/nyt.txt', 'a') as f:
            for url in links:
                f.write(url + '\n')


def reuters_gen(start, end):
    """
    functions creates all the reuters sitemap links within set range
    start / date datetime object
    """
    # get the date ranges
    times = [start]
    # since reuters does daily sitemaps, this one steps one day at a time
    while start <= end:
        start += timedelta(days=1)
        times.append(start)
    alpha_omega = {}
    for ii in range(0, len(times)-1):
        alpha_omega[times[ii]] = times[ii+1]
    # create the links
    hold_links = [] # list to hold the urls from the loop
    for k, v in alpha_omega.items():
        # changes out datetime object to a string in the same format as the Reuters url
        date1 = k.strftime("%Y%m%d")
        date2 = v.strftime("%Y%m%d")
        # Add the sitemap url to our list
        hold_links.append(f'https://www.reuters.com/sitemap_{date1}-{date2}.xml')
    return hold_links


def reuters_collect():
    """
    main function for collecting reuters links
    """
    # sitemaps start in 2006
    reu_sitemaps = reuters_gen(datetime(2006, 9, 22), datetime(2018, 12, 1))
    # collect the data
    for sm in tqdm(reu_sitemaps):
        try:
            urls = read_sitemap(sm)
            # write to a file
            with open('links/reuters.txt', 'a') as f:
                for url in reu_urls:
                    f.write(f'{url}\n')
        except urllib.error.HTTPError:
            pass


# ------------------------------------------------------------------------------
# functions for pulling info from the page
# ------------------------------------------------------------------------------

def nyt_story(html):
    """
    Function to pull the information we want from NYT stories

    Keyword arguments:
    html -- locallay saved or pre-downloaded html
    """
    # create a dictionary to hold everything in
    hold_dict = {}
    # first turn the html into BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')
    # pull the data I want
    # all the initial data I want is in the header so I restrict my search
        # so as to not accidentially pull in other  data
    header = soup.find('article').find('header')
    # title
    hold_dict['title'] = header.find('h1', itemprop='headline').text
    # authors
    authors_html = header.find('p', itemprop='author creator')
    hold_dict['authors'] = [tag.text for tag in authors_html.find_all('span', itemprop='name')]
    # date
    hold_dict['date'] = header.find('time')['datetime']
    # text
    article_body = soup.find('section', itemprop='articleBody')
    hold_dict['paragraphs'] = [paragraph.text for paragraph in article_body.find_all('p')]
    # location
    if '—' in paragraphs[0]:
        location = paragraphs[0].split('—')[0] # I take everything before the '—' in the first paragraph
    else:
        location = ''
    # images (in order)
        # beautifulsoup has a had time with the data-testid so I used an alternate way to search
    images = soup.find_all('div', {'data-testid':'photoviewer-wrapper'})
    hold_dict['image_urls'] = [image.find('img')['src'] for image in images]
    # captions (in order)
    hold_dict['image_captions'] = [image.find('figcaption', itemprop='caption description').text for image in images]
    # return
    return(hold_dict)


def reuters_story(html):
    """
    Function to pull the information we want from Retuers stories
    """
    # create a dictionary to hold everything in
    hold_dict = {}
    # first turn the html into BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')
    # pull the data I want
    # all the initial data I want is in the header so I restrict my search
        # so as to not accidentially pull in other  data
    header = header = soup.find('div', {'class':'ArticleHeader_container'})
    # title
    hold_dict['title'] = header.find('h1', {'class':'ArticleHeader_headline'}).text
    # authors
    authors = header.find('div', {'class':'BylineBar_byline'})
    hold_dict['authors'] = [author.text for author in authors.find_all('a')]
    # date
    hold_dict['date'] = header.find('div', {'class':'ArticleHeader_date'}).text
    # section
    hold_dict['section'] = header.find('div', {'class':'ArticleHeader_channel'}).text
    # text
    body = soup.find('div', {'class':'StandardArticleBody_body'})
    hold_dict['text'] = [paragraph.text.strip() for paragraph in body.find_all('p')
                         if not paragraph.has_attr('class')]
    # images (in order)
    image_containers = body.find_all('div', {'class':'Image_container'})
    images = [image.find('div', {'class':re.compile('LazyImage_image')}) for
              image in image_containers]
    hold_dict['image_urls'] = [re.search(r'\((.*?)\)', image['style']).group(1) for
                               image in images]
    # captions (in order)
    hold_dict['image_captions'] = [image.find('div', {'class':'Image_caption'}).text
                                   for image in image_containers]
    # return
    return hold_dict

def businessnews_story(html):
    # create a dictionary to hold everything in
    hold_dict = {}
    # first turn the html into BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    
    # title
    hold_dict['title'] = soup.find('h1', {'class':'headline'}).text

    # date
    date = soup.find('div', {'id':'post-info-left'}).text
    hold_dict['date'] = date.split("on")[-1]
    '''
    #author
    hold_dict["author"]= soup.find('div', {'class':'mvp-author-info-name left relative'}).text
    '''
    # Section is written just before the title which is at the end. This captures section.
    section = soup.find('div', {"id": "crumbs"}).text
    hold_dict['section'] = section.split(">")[-2]

    # text
    body = soup.find('div', {'id':'content-area'})
    text = [paragraph.text for paragraph in body.find_all('p') if not paragraph.has_attr('class')]
    # removing \xa0 s which are at the end mostly.
    text = [ii.replace("\xa0", "") for ii in text]
    # getting rid of empy strings
    text = list(filter(None, text))
    # some news are from other news sources which are indicated with [] at the end. Getting rid of those
    text = [item for item in text if not (item.startswith('[') and item.endswith(']'))]
    hold_dict['text'] = text

    # images (in order): this website does not use images. Rarely, they use them but they are included as paragraph items and they do not have separate tags.
    #hold_dict['image_urls'] = soup.find('div', {'class':'left relative mvp-post-feat-img-wide2'})
    # return
    return hold_dict

url = 'http://businessnews.com.ng/2017/06/02/no-date-for-budget-assent-presidency/'
hdr = {'User-Agent': 'Mozilla/5.0'} #known browser is needed for website, otherwise I got an forbidden error
request=urllib.request.Request(url, None, hdr) #The assembled request
html = urllib.request.urlopen(request)
businessnews_ng=businessnews_story(html)
