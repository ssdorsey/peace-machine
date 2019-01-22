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


def bamada_story:
#Bamada:
#Note: website is in French.
#No sitemap.
#sampleurl = 'http://bamada.net/le-ministre-nango-dembele-face-aux-acteurs-de-la-filiere-mangue-a-sikasso-il-ne-saurait-y-avoir-de-mangues-de-bonne-qualite-sans-vergers-exempts-de-toute-infestation-des-mouches'

#bamada.net/robots.txt:

"""
User-agent: *
# On empÃªche l'indexation des dossiers sensibles
Disallow: /cgi-bin
Disallow: /wp-admin
Disallow: /wp-includes
Disallow: /wp-content/plugins
Disallow: /wp-content/cache
Disallow: /wp-content/themes
Disallow: /trackback
Disallow: /feed
Disallow: /comments
Disallow: /category/*/*
Disallow: */trackback
Disallow: */feed
Disallow: */comments
Disallow: /*?*
Disallow: /*?
# On autorise l'indexation des images
Allow: /wp-content/uploads
User-agent: Googlebot
# On empÃªche l'indexation des fichiers sensibles
Disallow: /*.php$
Disallow: /*.js$
Disallow: /*.inc$
Disallow: /*.css$
Disallow: /*.gz$
Disallow: /*.swf$
Disallow: /*.wmv$
Disallow: /*.cgi$
Disallow: /*.xhtml$
# Autoriser Google Image
User-agent: Googlebot-Image
Disallow:
Allow: /*
# Autoriser Google AdSense
User-agent: Mediapartners-Google*
Disallow:
Allow: /*
# On indique au spider le lien vers notre sitemap
Sitemap: http://bamada.net/sitemapindex.xml
"""

	hold_dict = {}

	req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
	html = urllib.request.urlopen(req).read()
	soup = BeautifulSoup(html, 'lxml')

	#get title. this works.
	title_box = soup.find('h3',{'id':'post-title'})
	hold_dict['title'] = title_box.text.strip() #strip() is used to remove starting and trailing

	#get the authors
	author_date_box = soup.find('div', {'class': 'post-info'})
	authors_box = author_date_box.find("a")
	hold_dict['authors'] = authors_box['title'].strip()

	#get the date. Note: format dd/mm/yyyy
	hold_dict['date'] = author_date_box.contents[3].text.strip()

	#get the section
	section_box = soup.find('h5',{'class':'site-description'})
	hold_dict['section'] = section_box.text.strip()

	#no reported location

	#get the text
	text_box = soup.find('div', attrs={'id':'article'})
	hold_dict['text'] = text_box.text.strip()

	#get the first paragraph
	#it's surrounded by the <span> and </span> tags. I think the below code is right.
	hold_dict['first_paragraph'] = soup.find('div', id="article").p.text.strip()

	#get the images. This doesn't work all the time, the subject of the regex isn't always consistent.
	image_box = soup.find_all('img', {'class':re.compile('align')})
	hold_dict['image_urls'] = [image['src'] for image in image_box if 'jpg' in image['src']]

	#don't seem to be any captions.

    return hold_dict

def malijet_story(url):

	#sampleurl: http://malijet.com/les_faits_divers_au_mali/221481-bamako-des-hommes-arm%C3%A9s-cambriolent-la-station-%26amp%3Bquot%3Bbaraka-.html
	
	#create a dictionary to hold everything in
	hold_dict = {}

	req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
	html = urllib.request.urlopen(req).read()
	soup = BeautifulSoup(html, 'lxml')

	#get title
	title_box = soup.find('h1', attrs={'class':'page_title'})
	hold_dict['title'] = title_box.text.strip() #strip() is used to remove starting and trailing

	#get the authors
	authors_box = soup.find('span', attrs={'class':'story_author'})
	hold_dict['authors'] = authors_box.text.strip()

	#get the date. note: weird format.
	date_box = soup.find('span', attrs={'class':'story_date'})
	hold_dict['date'] = date_box.text.strip()

	#get section. get more specific here.
	section_box = soup.find('div', attrs={'class':'box_breadcrumb'})
	hold_dict['sections'] = section_box.find_all('a')[-1].text.strip()

	#get the article abstract
	abstract_box = soup.find('p', attrs={'class':'article_abstract'})
	hold_dict['abstract'] = abstract_box.text.strip()

	#get the text.
	text_box = soup.find('div', attrs={'id':'article_body'})
	hold_dict['text'] = [paragraph.text.strip() for paragraph in text_box.find_all('p') if not paragraph.has_attr('class')]

	#get first nonempty paragraph after the abstract
	hold_dict['first_paragraph'] = [paragraph.text.strip() for paragraph in text_box.find_all('p') if paragraph.text.strip() != ''][1]

	#no reported location for this publication.

	#get the images
	image_box = soup.find_all('img', attrs={'class':'img-responsive img-rounded'})
	hold_dict['image_urls'] = [image['src'] for image in image_box if 'article' in image['src']]

	#get the captions
	caption_box = soup.find_all('span', attrs={'class':'image_caption'})
	hold_dict['image_captions'] = [caption.text for caption in caption_box]

    return hold_dict

def Guardian_story(url):

	url = 'https://www.theguardian.com/world/2019/jan/18/zimbabwe-activists-protests-crackdown-spectre-of-mugabe-era'
	#url = 'https://www.theguardian.com/world/2019/jan/18/fiji-urges-australia-not-to-put-coal-above-pacific-nations-battling-climate-change'
	#create a dictionary to hold everything in
	hold_dict = {}

	req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
	html = urllib.request.urlopen(req).read()
	soup = BeautifulSoup(html, 'lxml')

	#get title
	title_box = soup.find('h1', attrs={'class':'content__headline '})
	hold_dict['title'] = title_box.text.strip() #strip() is used to remove starting and trailing

	#get the authors. not all articles have authors, especially wire reports.
	hold_dict['authors'] = list(set([a.text.strip() for a in soup.find_all('span', attrs={'itemprop':'name'})]))

	#get the date.
	date_box = soup.find('time', attrs={'class':re.compile('content__dateline')})
	hold_dict['date'] = date_box.text.strip()

	#get section
	section_box = soup.find('span', attrs={'class':'label__link-wrapper'})
	hold_dict['section'] = section_box.text.strip()

	#get the text.
	text_box = soup.find('div', attrs={'class':re.compile('content__article-body')})
	hold_dict['text'] = [p.text.strip() for p in text_box.find_all('p')]

	#get the article first paragraph
	abstract_box = soup.find('div', attrs={'class':'content__standfirst'})
	hold_dict['abstract'] = abstract_box.text.strip()

	#no reported location for this publication.

	#get the images
	image_box = soup.find_all('img',attrs={'class':'gu-image'})
	hold_dict['image_urls'] = [i['src'] for i in image_box]

	#get the captions
	caption_box = soup.find_all('figcaption', attrs={'class':re.compile('caption')})
	hold_dict['image_captions'] = [caption.text.strip() for caption in caption_box]

	return hold_dict

def wapo_story(url):

	#url = 'https://www.washingtonpost.com/local/immigration/getting-through-the-border-fence-was-easy-winning-the-right-to-stay-wont-be/2019/01/17/980ec59a-03ce-11e9-b5df-5d3874f1ac36_story.html?utm_term=.494b209cecdd'

	#create a dictionary to hold everything in
	hold_dict = {}

	req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
	html = urllib.request.urlopen(req).read()
	soup = BeautifulSoup(html, 'lxml')

	#get title
	title_box = soup.find('h1', attrs={'data-pb-field':'custom.topperDisplayName'})
	hold_dict['title'] = title_box.text.strip() #strip() is used to remove starting and trailing

	#get the authors
	hold_dict['authors'] = list(set([a.text.strip() for a in soup.find_all('a', attrs={'class':'author-name'})]))

	#get the date.
	date_box = soup.find('span', attrs={'itemprop':'datePublished'})
	hold_dict['date'] = date_box.text.strip()

	#get section
	section_box = soup.find('a', attrs={'class':'kicker-link'})
	hold_dict['section'] = section_box.text.strip()

	#get the article first paragraph
	abstract_box = soup.find('p', attrs={'data-elm-loc':'1'})
	hold_dict['abstract'] = abstract_box.text.strip()

	#get the text.
	text_box = soup.find('article', attrs={'itemprop':'articleBody'})
	hold_dict['text'] = [p.text.strip() for p in text_box.find_all('p')]

	#no reported location for this publication.

	#get the images
	image_box = [x.find('img',attrs={'class':'unprocessed'}) for x in soup.find_all('div',attrs={'class':re.compile('inline-content')}) if x.find('img',attrs={'class':'unprocessed'})]
	hold_dict['image_urls'] = [i['data-hi-res-src'] for i in image_box]

	#get the captions
	caption_box = soup.find_all('span', attrs={'class':re.compile('pb-caption')})
	hold_dict['image_captions'] = [caption.text.strip() for caption in caption_box]

	return hold_dict

