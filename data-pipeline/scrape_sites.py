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
import bs4
import numpy as np


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

    return hold_dict

def star_story(html):
    '''
    url = 'https://www.the-star.co.ke/news/2018/12/14/knut-rejects-uhurus-big-4-housing-levy_c1865754'
    '''
    hold_dict={}
    soup=BeautifulSoup(html, 'lxml')
    header=soup.find('div', {'class':'l-region l-region--title'})
    hold_dict['title']=header.find('div', {'class':'pane-content'}).text.strip()
    header_auth=soup.find('div', {'class':'panel-pane pane-entity-field pane-node-field-converge-byline'})
    hold_dict['authors']=header_auth.find('div', {'class':'field__item even'}).text[3:].split(' and ')
    hold_dict['date']=header.find('div', {'class':'field__item even'}).text
    hold_dict['section']=header_section.find('a',{'href':'/sections/national-news_c29654'}).text
    body=soup.find('div', {'class':'field field-name-body'})
    hold_dict['text']= [paragraph.text for paragraph in body.find_all('p')]
    image_containers = soup.find_all('div', {'class':'panel-pane pane-page-content'})
    hold_dict['image']= [image.find('div', {'class':re.compile('field__item even')}) for
              image in image_containers]
    hold_dict['srcs'] = [img['src'] for img in soup.find_all('img')]
    hold_dict['alts'] = [img['alt'] for img in soup.find_all('img')]

    return hold_dict


def nan_story(html):
    """
    There is no information for the sitemap when using https://www.nan.ng/robots.txt
    Caption info is messy
    url_1 = 'https://www.nan.ng/news/jonathan-visited-buhari/'
    """
    hold_dict={}
    soup=BeautifulSoup(html, 'lxml')
    header=soup.find('div', {'class':'article-header none'})
    hold_dict['title'] = header.find('h1', {'class':' xt-post-title'}).text.strip()
    hold_dict['date'] = soup.find('time', {'class':' xt-post-date'})['datetime'].split('T')[0]
    body=soup.find('div',{'class':'article-content'})
    firstline = body.find('p').text
    if firstline.startswith('By'):
        hold_dict['authors'] = body.find('p').getText().split('By')[1].split('/')
    else:
        hold_dict['authors'] = ['']
    if firstline.startswith('By'):
        hold_dict['text'] = [paragraph.text for paragraph in body.find_all('p') if not paragraph.has_attr('class')][1:]
    else:
        hold_dict['text'] = [paragraph.text for paragraph in body.find_all('p') if not paragraph.has_attr('class')][0:]
    if body.find_all('img'):
         images=[img['src'] for img in body.find_all('img')]
    hold_dict['caption'] = soup.find_all('figcaption', {'class':'wp-caption-text'})
    return hold_dict


def thenews_story(html):
    """
    There is no information for the sitemap when using https://www.nan.ng/robots.txt
    url = 'https://www.thenewsnigeria.com.ng/2019/01/i-can-vouch-for-atiku-says-obasanjo/'
    """
    hold_dict={}
    soup=BeautifulSoup(html, 'lxml')
    header=soup.find('div', {'id':'content'})
    hold_dict['title']=header.find('h1', {'class':'entry-title single-entry-title'}).text.strip()
    hold_dict['date']=header.find('div', {'class':'info'}).text.strip().split(" -")[0]
    news_section=soup.find('div',{'class':'single-category'})
    hold_dict['section']=news_section.find('ul',{'class':'post-categories'}).text.strip().split('\n')
    body=soup.find('div',{'class':'entry-content'})
    hold_dict['text'] = [paragraph.text.strip() for paragraph in body.find_all('p') if not paragraph.has_attr('class')]
    if hold_dict['text'][-1].startswith('('):
        hold_dict['authors'] = hold_dict['text'][-1]
    else:
        hold_dict['authors']=[""]
    if body.find_all('img'):
         hold_dict['images'] = [img['src'] for img in body.find_all('img')]
    if soup.find('p', {'class': re.compile(r'caption')}):
        hold_dict['caption'] = soup.find('p', {'class': re.compile(r'caption')}).text
    else:
        hold_dict['caption'] = ['']
    return hold_dict

def ndn_story(html):
    """
    There is no information for the sitemap when using https://www.nan.ng/robots.txt
    Section is messy, when multiple section couldn't divide them
    Images have no captions
    url = 'http://nationaldailyng.com/code-of-conduct-tribunal-vs-saraki-free-speech-and-politics-of-contempt/'
    """
    hold_dict={}
    soup=BeautifulSoup(html, 'lxml')
    header=soup.find('div', {'class':'td-post-header'})
    hold_dict['title']=header.find('h1', {'class':'entry-title'}).text.strip()
    hold_dict['date']=header.find('div', {'class':'td-post-date'}).text
    hold_dict['authors']= header.find('div',{'class':'td-post-author-name'}).text.strip().split('By')[1].split('-')[0]
    hold_dict['section']=header.find('ul', {'class':'td-category'}).text
    picture=soup.find('div',{'class':'td-post-featured-image'})
    if soup.find('div', {'class':'td-post-featured-image'}):
        hold_dict['images'] = [img['src'] for img in picture.find_all('img')]
    body=soup.find('div',{'class':'td-post-content'})
    paragraphs=[paragraph.text.strip() for paragraph in body.find_all('p')]
    if paragraphs==[]:
        text=[paragraph.text.strip() for paragraph in body.find_all('span')]
        hold_dict['text']=list(filter(None, text))
    else:
        hold_dict['text']=body_p=list(filter(None, paragraphs))
    return hold_dict


def tdn_story(html):
    """
    Unable to strip the time from the date
    The html for the image is incomplete in the website it lacks www.businessdailyafrica.com, not sure if how I did it is the most efficient
    sitemap = https://www.businessdailyafrica.com/sitemap-index.xml
    just tested with 5 recent ones
    url = 'https://www.businessdailyafrica.com/economy/Transport-minister-now-suspends-car-free-day/3946234-4958954-qhf99lz/index.html'
    """
    hold_dict={}
    soup=BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h2', {'class':'article-title'}).text
    hold_dict['date'] =soup.find('small', {'class':'byline'}).text
    hold_dict['authors'] = soup.find('header', {'class':'article-meta-summary'}).text.strip().split('By ')[1].split('\n')[0]
    mainpic = soup.find('figure', {'class':'article-img-story'})
    if soup.find('figure', {'class':'article-img-story'}):
        src = [img['src'] for img in mainpic.find_all('img')]
        src.insert(0, 'www.businessdailyafrica.com')
        hold_dict['images'] = [''.join(src[0:])]
    else:
        hold_dict['images'] = []
    # Caption
    hold_dict['caption'] = soup.find('figcaption',{'class':'attribution'}).text.strip().split('FILE PHOTO')[0]
    # Text
    body = soup.find('article',{'class':'article-story page-box'})
    hold_dict['text'] = [paragraph.text.strip() for paragraph in body.find_all('p')]
    # section
    hold_dict['section'] = [caption.text.strip() for caption in body.find_all('h5')][0]
    return hold_dict


def cit_story(html):
    '''
    url = 'https://citizentv.co.ke/news/wambora-governor-with-9-lives-says-impeachment-attempts-have-taught-him-resilience-229263/'
    '''
    hold_dict = {}
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class': 'articleh1'}).text
    hold_dict['authors'] = soup.find('span', {'itemprop':'name'}).text
    hold_dict['date'] = " ".join(soup.find('span', {'class':'date-tag'}).text.split(" ")[0:3])
    body = soup.find('span', {'itemprop':'description'}).find_all('p', recursive=False)
    pars = [paragraph.text.encode('ascii', 'ignore').decode() for paragraph in body][:-1]
    hold_dict['paragraphs'] = list(filter(None, pars))
    img = [i.find('img') for i in soup.find_all("figure")]
    captions = [i.find('figcaption') for i in soup.find_all("figure")]
    if img:
         hold_dict['image_urls'] = [img[0]['src']]
    else:
        hold_dict['image_urls'] = []
    if len(img) > 1:
         hold_dict['image_urls'].append([i['data-lazy-src'] for i in img[1:]])
    if captions:
         hold_dict['image_captions'] = [c.text.strip() for c in captions]
    return(hold_dict)


def bt_story(html):
    """
    I have an issue with the text, I wasn't able to take out some of the links in the paragraph because they are imbedded in paragraphs
    not sure why some images don't get scraped https://businesstoday.co.ke/october-inflation-5-53-food-electricity-prices-drop/ or https://businesstoday.co.ke/beta-healthcare-blames-promiscuous-man-condom-burst-case/
    url = 'https://businesstoday.co.ke/cheap-commonly-used-physical-health-drugs-can-help-treat-mental-illness/'
    """
    hold_dict={}
    soup=BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('span', {'class':'post-title'}).text.strip()
    hold_dict['date'] = soup.find('span', {'class':'time'}).text.split('On ')[1]
    hold_dict['authors'] = soup.find('span',{'class':'post-author-name'}).text.strip().split('By ')[1]
    img = [i.find('img') for i in soup.find_all("figure")]
    if img:
         hold_dict['images'] = [img[0]['src']]
    else:
        hold_dict['images'] = []
    captions = [i.find('figcaption') for i in soup.find_all("figure")]
    if captions:
         hold_dict['caption'] = [c.text.strip() for c in captions]
    else:
        hold_dict['caption'] = ['']
    body = soup.find('div', {'class':'entry-content clearfix single-post-content'})
    # pars = [paragraph.text.encode('ascii', 'ignore').decode() for paragraph in body if not paragraph.has_attr('a')]
    # hold_dict['text'] = pars
    hold_dict['section'] = soup.find('div',{'class':'term-badges floated'}).text.strip()
    return hold_dict



def devex_story(html):
    """
    weird symbols within the text, usually slashes not in all of them
    tested historically
    url = 'https://www.devex.com/news/brazil-49844'
    """
    hold_dict={}
    soup=BeautifulSoup(html, 'lxml')
    hold_dict['title'] =soup.find('h1', {'itemprop': 'headline'}).text.strip()
    hold_dict['date'] = soup.find('span', {'itemprop':'dateCreated'}).text
    hold_dict['authors'] = soup.find('a', {'itemprop':'name'}).text
    img = [i.find('img') for i in soup.find_all("figure")]
    if img:
         hold_dict['images'] = [img[0]['src']]
    else:
        hold_dict['images'] = []
    captions = [i.find('figcaption') for i in soup.find_all("figure")]
    if captions:
         hold_dict['caption'] = [c.text.strip() for c in captions]
    else:
         hold_dict['caption'] = ['']
    body = soup.find('div', {'class':'article-content'}).find_all('p', recursive=False)
    hold_dict['text'] = [paragraph.text.encode('ascii', 'ignore').decode() for paragraph in body]
    categories = soup.find('ul', {'class':'categories'})
    hold_dict['section'] =[sec.text for sec in categories.find_all('li')]
    return hold_dict


def standard_story(html):
    """
    url='https://www.standardmedia.co.ke/article/2001306089/raila-hosts-uhuru-in-first-kisumu-visit-since-handshake'
    url = "https://www.standardmedia.co.ke/health/article/2001311787/kibra-mp-i-cannot-be-cured-but-i-will-manage-my-cancer"
    url = "https://www.standardmedia.co.ke/article/2001304249/what-to-do-to-ensure-affordable-housing-fund-gets-critical-buy-in"
    """
    hold_dict={}
    soup=BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class':'article-title'}).text.strip()
    hold_dict['date'] = soup.find('li', {'style':'font-size: 10px'}).text.strip().split('Posted on: ')[1].split(' GMT')[0]
    hold_dict['authors'] = soup.find('ul', {'class':'article-meta'}).text.strip().split('\n')[0].split(' and ')
    sec = soup.find('ol',{'class':'breadcrumb'}).text.strip().split('\n')
    hold_dict['section'] = [s for s in sec if s] # careful, previous one returned filter object
    img = soup.find_all("figure")
    if img:
        src = [i.find('img')['src'] for i in img]
        src.insert(0, 'www.standardmedia.co.ke')
        hold_dict['image'] = ''.join(src)
    captions = soup.find_all("figcaption")
    if captions:
        hold_dict['caption'] = [c.text.strip() for c in captions]
    else:
        hold_dict['caption'] = ['']
    body = soup.find('div', {'class':'article-body'}).text
    body = body.split('\n')
    body = [s.rstrip() for s in body if hold_dict['date'] not in s and hold_dict['authors'][0] not in s \
                                    and hold_dict['title'] not in s and 'SEE ALSO' not in s and 'function()' not in s]
    if hold_dict['caption'][0] is not '':
        body = [s for s in body if hold_dict['caption'][0] not in s]
    hold_dict['text'] = list(filter(None, body))
    return hold_dict


def nwn_story(html):
    """
    There is no caption for the pictures
    url = 'https://politicsngr.com/apc-governorship-aspirant-backs-direct-primaries/'
    """
    hold_dict={}
    soup=BeautifulSoup(html, 'lxml')
    header=soup.find('header', {'id':'mvp-post-head'})
    hold_dict['title']=header.find('h1', {'class':'mvp-post-title left entry-title'}).text.strip()
    hold_dict['date']=header.find('span', {'class':'mvp-post-date updated'}).text.strip()
    hold_dict['authors']= header.find('div', {'class':'mvp-author-info-name left relative'}).text.strip().split('By ')[1]
    hold_dict['section']=header.find('h3', {'class':'mvp-post-cat left relative'}).text.strip()
    body=soup.find('div', {'id':'mvp-content-main'})
    mainpic=soup.find('div',{'id':'mvp-post-feat-img'})
    feat_img=[img['src'] for img in mainpic.find_all('img')]
    other_img=[img['src'] for img in body.find_all('img')][:-2]
    if other_img==[]:
        hold_dict['images'] =feat_img
    else:
        hold_dict['images'] = [feat_img, other_img]
    text = [paragraph for paragraph in body.find_all('p')]
    text = [p.text for p in text if not p.find('style')]
    text = [p.split('\n') for p in text]
    text = [item for sublist in text for item in sublist]
    text = [' '.join(t.split()) for t in text]
    hold_dict['text']=list(filter(None, text))
    return hold_dict


def dnt_story(html):
    """
    There is no caption for the pictures or section
    There is no information for the sitemap when using https://www.dailynews.co.tz/robots.txt
    If the images are broken the image link is empty
    url = 'https://www.dailynews.co.tz/news/kisutu-court-acquits-tbc1-presenter-jerry-muro.aspx'
    """
    hold_dict={}
    soup=BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h4',{'class':'entry-title'}).text.strip()
    hold_dict['date'] = soup.find('div', {'class':'post-meta-date'}).text
    firstline = soup.find('div',{'class':'post-meta-author'}).text.strip()
    if firstline.startswith('By'):
        hold_dict['authors'] = soup.find('div',{'class':'post-meta-author'}).text.strip().split('By ')[1]
    else:
        if firstline.startswith('From'):
            hold_dict['authors'] = soup.find('div',{'class':'post-meta-author'}).text.strip().split('From ')[1].split('in')[0]
        else:
            hold_dict['authors'] = firstline
    mainpic = soup.find('div',{'class':'entry-media'})
    hold_dict['images'] = [img['src'] for img in mainpic.find_all('img')]
    body = soup.find('div', {'class':'entry-content'})
    text = [paragraph for paragraph in body.find_all('p')]
    text = [item for sublist in text for item in sublist]
    pars = [p.strip().encode('ascii', 'ignore').decode() for p in text if type(p) is bs4.element.NavigableString]
    hold_dict['text'] = list(filter(None, pars))
    return hold_dict


def fh_story(html):
    """
    Taking only first author when multiple, too inconsistent to get all
    No visible section in the webpage
    url = 'https://freedomhouse.org/blog/elections-togo-what-happens-when-world-isn-t-watching'
    url = "https://freedomhouse.org/blog/ethiopia-attack-civil-society-escalates-dissent-spreads"
    """
    hold_dict={}
    soup=BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1',{'class':'title'}).text
    hold_dict['date'] = soup.find('div', {'class':'field field-name-post-date field-type-ds field-label-hidden'}).text
    body = soup.find('div', {'class':'field field-name-body field-type-text-with-summary field-label-hidden'})
    pars = [paragraph.text.encode('ascii', 'ignore').decode() for paragraph in body.find_all('p')]
    hold_dict['text'] = list(filter(None, pars))
    if len(pars)>1 and re.match('by', pars[0], re.IGNORECASE):
        authors = re.sub('by', '', pars[0].encode('ascii', 'ignore').decode().replace('\n', ' '), re.I)
        hold_dict['authors'] = authors.split(',')[0]
        hold_dict['text'] = hold_dict['text'][1:]
    elif soup.find('div', {'class': 'field field-name-field-blog-author field-type-text-long field-label-hidden'}):
        hold_dict['authors'] = soup.find('div', {'class': 'field field-name-field-blog-author field-type-text-long field-label-hidden'}).text.split('by ')[1].split(',')[0]
    else:
         hold_dict['authors'] = []
    img = soup.find('div', {'class':'grid-20 region region-content'}).find_all('img')
    if img:
        hold_dict['images'] = [i['src'] for i in img]
    else:
        hold_dict['images'] = []
    captions = soup.find(class_="image-field-caption")
    if captions:
        hold_dict['captions'] = captions.text.strip()
    else:
        hold_dict['captions'] = []
    return hold_dict
