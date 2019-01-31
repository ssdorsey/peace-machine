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


def aljazeera_gen(year):
    """
	Note: the sitemap for al jazeera is split by year. Creates date-formatted
	links to the aljazeera sitemaps
    """
    return f'https://www.aljazeera.com/xml/sslsitemaps/sitemap{year}_1.xml'


def collect_aljazeera():
    """
    main function to collect all the AJ links. sitemap urls only contain years, not months,
    so comment out the months below. 
    """
    # all the years we want from AJ -- only have sitemaps from 2003 on. 
    years = range(2003, 2019)
    # all the months we want from AJ
    #months = range(1, 13)
    # create a list of all the sitemap urls
    aljazeera_sitemaps = [aljazeera_gen(year) for year in years]
    # loop through every sitemap and get the links
    for sm in tqdm(aljazeera_sitemaps): # tqdm just gives us an easy progress tracker
        links = read_sitemap(sm)
        # save the links to a text file
        with open('links/aljazeera.txt', 'a') as f:
            for url in links:
                f.write(url + '\n')
		
def dw_gen(start_month, start_year, end_month, end_year):
    """
    creates date-formatted links to the dw sitemaps
    """
    # checks for a 2-digit month format, ex: '02'
    if not type(start_month) is str:
        start_month = str(start_month)
        start_month = f'{start_month:02}'
        # if len(start_month) < 2:
        #     start_month = '0' + start_month
    if not type(end_month) is str:
        end_month = str(end_month)
        end_month = f'{end_month:02}'
        # if len(start_month) < 2:
        #     start_month = '0' + start_month
    return f'https://www.dw.com/en/sitemap-detail-from-{start_year}-{start_month}-01-to-{end_year}-{end_month}-01.xml'


def collect_dw():
    """
    main function to collect all the dw links
    """
    # all the months and years we want from DW
    m = range(1, 13)
    startyear = 2002
    endyear = 2020
    numyears = endyear - startyear
    nummonths = numyears * 12
    #get the months and years in right quarterly format
    mth = [month % 12 + 1 for month in range(0,nummonths)]
    mth = [f'{month:02}' for month in mth]
    yr = [month // 12 + startyear for month in range(0,nummonths)]
    date = pd.DataFrame({'mth':mth,'yr':yr})
    date = date[(date['mth'] == '01') | (date['mth'] == '04') | (date['mth'] == '07') | (date['mth'] == '10')]
    date = date[:-2]
    #make each month variable
    start_month = [date['mth'].iloc[d] for d in range(0, len(date['mth']))]
    start_year = [date['yr'].iloc[d] for d in range(0, len(date['mth']))]
    end_month = [date['mth'].iloc[d] for d in range(1, len(date['mth']))]
    end_year = [date['yr'].iloc[d] for d in range(1, len(date['mth']))]
    # create a list of all the sitemap urls
    dw_sitemaps = [dw_gen(start_month[i], start_year[i], end_month[i], end_year[i]) for i in range(len(end_month))]
    # loop through every sitemap and get the links
    for sm in tqdm(dw_sitemaps): # tqdm just gives us an easy progress tracker
        links = read_sitemap(sm)
        # save the links to a text file
        with open('links/dw.txt', 'a') as f:
            for url in links:
                f.write(url + '\n')


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

	hold_dict = {}

	req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
	html = urllib.request.urlopen(req).read()
	soup = BeautifulSoup(html, 'lxml')

	#get title. 
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

	#url = 'https://www.theguardian.com/world/2019/jan/18/zimbabwe-activists-protests-crackdown-spectre-of-mugabe-era'
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

def aljazeera_story(url):

	#url = 'https://www.aljazeera.com/news/2019/01/sudan-targets-demonstrators-journalists-protests-continue-190122151114041.html'
	#url = 'https://www.aljazeera.com/news/2019/01/manbij-attack-calls-turkey-cooperation-syria-190117104601190.html'

	#create a dictionary to hold everything in
	hold_dict = {}

	req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
	html = urllib.request.urlopen(req).read()
	soup = BeautifulSoup(html, 'lxml')

	#get title
	title_box = soup.find('h1', attrs={'class':'post-title'})
	hold_dict['title'] = title_box.text.strip() #strip() is used to remove starting and trailing

	#get the authors. not all articles have authors, especially wire reports.
	hold_dict['authors'] = list(set([a.text.strip() for a in soup.find_all('a', attrs={'rel':'author'})]))

	#get the date.
	date_box = soup.find('div', attrs={'class':'article-duration'})
	hold_dict['date'] = date_box.text.strip()

	#get section
	section_box = soup.find('li', attrs={'id':'articlestoptopic'})
	hold_dict['section'] = section_box.text.strip()

	#get the text.
	text_box = soup.find('div', attrs={'class':'article-p-wrapper'})
	hold_dict['text'] = [p.text.strip() for p in text_box.find_all('p')]

	#get the article first paragraph
	abstract_box = soup.find('p', attrs={'class':'article-heading-des'})
	hold_dict['abstract'] = abstract_box.text.strip()

	#no reported location for this publication.

	#get the source
	source_box = soup.find('div', attrs={'class':'article-body-artSource'})
	hold_dict['Source'] = source_box.text.strip()

	#get the images
	image_box = soup.find_all('img',attrs={'class':re.compile('img-responsive')})
	hold_dict['image_urls'] = [i['src'] for i in image_box]

	#get the captions
	caption_box = soup.find_all('figcaption', attrs={'class':'main-article-caption'})
	hold_dict['image_captions'] = [caption.text.strip() for caption in caption_box]

	return hold_dict

def dw_story(html):
    """get story data for dw urls. """
    #url = 'https://www.dw.com/en/obasanjo-disputed-elections-are-better-than-no-elections/a-47181718'
    #url = 'https://www.dw.com/en/uk-pm-theresa-may-to-take-brexit-options-back-to-eu-negotiators/a-47170783'

    #create a dictionary to hold everything in
    hold_dict = {}

    #req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
    #html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html, 'lxml')

    #get title
    hold_dict['title'] = soup.find('h1').text.strip()

    #get the authors. not all articles have authors, especially wire reports.
    smallList = soup.find('ul', {'class':'smallList'})
    #author_box = str(set([x.text.strip() for x in soup.find_all('li') if re.match(r'Author\s+', x.text.strip())]))
    #rest = author_box.split('\\n', 1)[1]
    #hold_dict['author'] = rest.split(' (',1)[0]
    hold_dict['author'] = smallList.find(text='Author').parent.next_sibling.strip().split(',')

    #get the date. format dd.mm.yyyy
    #date_box = str(set([x.text.strip() for x in soup.find_all('li') if re.match(r'Date\s+', x.text.strip())]))
    #hold_dict['date'] = re.split('(\d{2}.\d{2}.\d{4})',date_box,1)[1]
    hold_dict['date'] = smallList.find(text='Date').parent.next_sibling.strip().split(',')

    #get section
    hold_dict['section'] = soup.find('h4', attrs={'class':'artikel'}).text.strip()

    #get the text.
    text_box = soup.find('div', attrs={'class':'longText'})
    hold_dict['text'] = [p.text.strip() for p in text_box.find_all('p')]

    #get the article first paragraph
    hold_dict['abstract'] = soup.find('p', attrs={'class':'intro'}).text.strip()

    #no reported location for this publication.

    #get the images
    image_box = [x for x in soup.find_all('a', attrs={'class':re.compile('overlayLink')}) if str(x).find('img') > 0]
    rest2 = [str(x).split('<img')[1] for x in image_box]
    srcs = [str(x).split('src="')[1] for x in rest2]
    hold_dict['image_urls'] = [str(x).split('" title=')[0] for x in srcs]

    #get the captions
    rest3 = [str(x).split('alt="')[1] for x in image_box]
    hold_dict['image_captions'] = [str(x).split('" ')[0] for x in rest3]

    return hold_dict

def france24_story(url):
	"""
	collecting story data for france 24. 
	can't figure out a good way to get images or captions to work for this one.
	"""

	url = 'https://www.france24.com/en/20190123-yellow-vests-french-riot-police-now-wear-body-cameras'

	#create a dictionary to hold everything in
	hold_dict = {}

	req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
	html = urllib.request.urlopen(req).read()
	soup = BeautifulSoup(html, 'lxml')

	#get title
	hold_dict['title'] = soup.find('h1', attrs={'class':re.compile('t-content__title')}).text.strip()

	#get the authors. not all articles have authors, especially wire reports.
	#soup.find_all('span',attrs={'class':'m-from-author__name'})
	hold_dict['author'] = str(set([x.text.strip() for x in soup.find_all('span',attrs={'class':'m-from-author__name'})]))
	# if re.match(r'Author\s+', x.text.strip())]))

	#get the date. format dd.mm.yyyy
	date_box = [x.text.strip() for x in soup.find_all('span',attrs={'class':'m-pub-dates__date'})]
	hold_dict['publish_date'] = date_box[0]
	hold_dict['latest_update_date'] = date_box[-1]

	#get section
	hold_dict['section'] = soup.find('a', attrs={'class':'m-breadcrumb__list__item__link'}).text.strip()

	#get the text.
	text_box = soup.find('div', attrs={'class':'t-content__body'})
	hold_dict['text'] = [p.text.strip() for p in text_box.find_all('p')]

	#get the article first paragraph
	hold_dict['abstract'] = soup.find('p', attrs={'class':'t-content__chapo'}).text.strip()

	#no reported location for this publication.

	#get the images
	#not done here yet
	# image_box = soup.find_all('div', {'class':'t-content__main-media'})
	# a = [x.find('img') for x in image_box]
	# b = [a.find('src') for x in a]
	# [x['src'] for x in soup.find_all('img', attrs={'class':'m-figure__img'})]
	#hold_dict['image_urls'] =

	#get the captions
	#not done here yet either, this will come with images.
	# hold_dict['image_captions'] = [str(x).split('" ')[0] for x in rest3]

	return hold_dict


def parse_almizan(html):
    '''
    Author a bit inconsistent but works.
    Date is in Islamic calendar
    url = "http://www.almizan.info/rht1360c.htm"
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    body = soup.find_all('p')
    pars = list(filter(None, [p.text.strip() for p in body][1:]))
    pars = sum([p.split('\n') for p in pars], [])
    hold_dict['title'] = pars[0]
    hold_dict['paragraphs'] = pars[1:]
    if soup.find('i'):
        hold_dict['authors'] = soup.find('i').text.replace('Daga ', '')
    hold_dict['date'] = soup.find('th').text.strip()
    img = soup.find(class_="sb_news_box_mine").find('img')
    if img:
        hold_dict['image_urls'] =  ''.join('http://almizan.info/' + img['src'])
    else:
        hold_dict['image_urls'] = []
    hold_dict['image_captions'] = []
    return(hold_dict)
    
    
def parse_aminiya(html):
    '''
    sitemap in: "https://aminiya.dailytrust.com.ng/sitemap_index.xml"
    Text can't be extracted from a few early stories.
    Text often separated by '<br/>', see split code below
    url = "https://aminiya.dailytrust.com.ng/dalilin-hadewarmu-don-kawar-da-gwamnan-bauchi-bello-kirfi/"
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class': 'entry-title'}).text.encode('ascii', 'ignore').decode()
    hold_dict['authors'] = soup.find('span', {'class':'author vcard'}).text.split(',')[0]
    hold_dict['date'] = soup.find('time', {'class':re.compile(r'entry-date')}).text
    body = soup.find('div', {'class':'entry-content'}).find_all('p')  
    pars = [i for list in body for i in list]
    pars = [p.encode('ascii', 'ignore').decode() for p in pars if type(p) is bs4.element.NavigableString] 
    hold_dict['paragraphs'] = list(filter(None, pars))
    img = soup.find_all('img', {'class':re.compile(r'wp-post-image')})
    if img:
        hold_dict['image_urls'] = [i['src'] for i in img]
    else:
        hold_dict['image_urls'] = []
    caption = soup.find_all('figcaption')
    if caption:
        hold_dict['image_captions'] = [c.text for c in caption]
    else:
        hold_dict['image_captions'] = []
    return(hold_dict)
    
    
    
def parse_kbc(html):
    '''
    KBC Kenya. site_url = "http://www.kbc.co.ke/sitemap_index.xml"
    url = "http://www.kbc.co.ke/cabinet-approves-establishment-of-counter-improvised-explosive-device-centre/"
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class': 'entry-title'}).text
    author_box = soup.find('div', {'class':'td-post-small-box'})
    if author_box:
        hold_dict['authors'] = author_box.find('a').text
    else:
        hold_dict['authors'] = []
    hold_dict['date'] = soup.find('time', {'class':'entry-date updated td-module-date'})['datetime'].split('T')[0]
    body = soup.find('div', {'class':'td-post-content'}).find_all('p') 
    pars = [paragraph.text.encode('ascii', 'ignore').decode() for paragraph in body]
    hold_dict['paragraphs'] = list(filter(None, pars))    
    img = soup.find('div', {'class':'td-post-featured-image'})
    if img:
        hold_dict['image_urls'] = [i['src'] for i in img.find_all('img')]
    else:
        hold_dict['image_urls'] = []
    captions = soup.find_all('figcaption')
    if captions:
        hold_dict['image_captions'] = [c.text.strip() for c in captions]
    else:
        hold_dict['image_captions'] = []
    return(hold_dict)
    


def parse_citizen(html):
    '''
    Citizen Kenya. Sitemap: "https://citizentv.co.ke/sitemap_index.xml"
    url = "https://citizentv.co.ke/sports/plane-cushions-found-in-search-for-footballer-sala-229191/"
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



def parse_guardianng(html):
    '''
    GUARDIAN NIGERIA. site_url = "https://guardian.ng/sitemap.xml"
    example url: https://guardian.ng/news/putin-warns-of-consequences-over-orthodox-split/        
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find(class_=re.compile(r'after-category')).text.replace("\xa0", "") 
    author = soup.find(class_=re.compile(r'author')).text.strip().replace("By ", "")
    hold_dict['authors'] = author.split(',')[0] # remove cities or positions
    hold_dict['date'] = ' '.join(soup.find(class_=re.compile(r'manual-age')).text.split())
    hold_dict['image_urls'] = []
    hold_dict['image_captions'] = []
    if soup.article.find_all('img'):
        hold_dict['image_urls'] = [i['src'] for i in soup.article.find_all('img') if '/plugins/' not in i['src']]
        captions = soup.find_all(class_=re.compile(r'caption'))
        hold_dict['image_captions'] = list(set([c.text.strip() for c in captions]))
    body = soup.find('article').text 
    hold_dict['paragraphs'] =  list(filter(None, body.split('\n'))) # getting paragraphs indexed by line breaks; if by 'p', first par is lost. Remove potential empty ones.
    if hold_dict['image_captions']:
        hold_dict['paragraphs'][0] = hold_dict['paragraphs'][0].replace(hold_dict['image_captions'][0], '') #remove caption match
        hold_dict['paragraphs'] = list(filter(None,  hold_dict['paragraphs'])) # Remove empty ones. Important to do this again in case all caption was first par  
    return(hold_dict)

    
def parse_punch(html):
    '''
    PUNCH NIGERIA. site_url = "https://punchng.com/sitemap.xml"
    example url: https://punchng.com/nigerian-air-force-redeploys-27-air-marshals-45-senior-officers/
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', class_='post_title').text    
    hold_dict['authors'] = []
    if soup.article.find("strong"):
        hold_dict['authors'] = soup.article.find("strong").text.split(',')[0]
    if "Copyright PUNCH." in hold_dict['authors'] or "READ ALSO" in hold_dict['authors']:
        hold_dict['authors'] = []
    hold_dict['date'] = soup.find('time', class_=re.compile(r'entry-date published')).text   
    pars = [paragraph.text.strip() for paragraph in soup.find('div', class_='entry-content').find_all('p')] # there were some empty paragraphs        
    if len(pars)==0: 
        pars = soup.find('div', class_='col-md-12 col-lg-8').find_all('div')
        pars = [p.text.replace("\n","") for p in pars]  
    if hold_dict['authors']:
        if hold_dict['authors'] in pars[0]:
            pars = pars[1:len(pars)]
    hold_dict['paragraphs'] =  list(filter(None, pars)) # assign pars and remove empty ones
    if ('AFP' or 'Reuters' or 'NAN' or 'AP') in pars[len(pars)-1]:
        hold_dict['authors'] = pars[len(pars)-1].replace('(', '').replace(')', '')
    image_url = soup.find_all('div', class_='blurry')[0]['style']
    hold_dict['image_urls'] = image_url[image_url.find("(")+2:image_url.find(")")-1] # can't split here, have to substring
    hold_dict['image_captions'] = []
    if soup.find('span', class_='caption'):
        hold_dict['image_captions'] = soup.find('span', class_='caption').text              
    return(hold_dict)


def parse_vanguard(html):
    '''
    VANGUARD NIGERIA. site_url = "http://www.vanguardngr.com/sitemap_index.xml"
    example url: https://www.vanguardngr.com/2019/01/video-kwara-apcs-governorship-candidate-abdulrazaq-shuts-down-ilorin/
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class': 'entry-title'}).text    
    if soup.find('time', {'class': 'entry-date published'}): # some don't have date
        hold_dict['date'] = soup.find('time', {'class': 'entry-date published'}).text
    else:
        hold_dict['date'] = soup.find('meta', property='article:published_time')['content'].split('T')[0]
    hold_dict['authors'] = []
    if soup.find('div', id="rtp-author-box"):
        hold_dict['authors'] = soup.find('div', id="rtp-author-box").find('h2').text # Is nested finds an elegant solution? 
    pars = [p.text for p in soup.find('article').find_all('p') if p.text is not ''] # there were some empty paragraphs
    if 'By' in str(pars[0:2]):     
        pos = int(np.where(["By" in s for s in pars[0:2]])[0])
        hold_dict['paragraphs'] = pars[pos+1:len(pars)]
        hold_dict['authors'] += ''.join(", " + pars[pos][3:len(pars[pos])])
    elif len(pars) is 0: 
        hold_dict['paragraphs'] = soup.find('article').text
    else:   
        hold_dict['paragraphs'] = pars
    if '\n' in hold_dict['authors']:
        hold_dict['paragraphs'] = [hold_dict['authors'].split('\n')[1]] + hold_dict['paragraphs']   
        hold_dict['authors'] = hold_dict['authors'].split('\n')[0]
    imgs = soup.article.find_all('img', class_=re.compile(r'size-full'))[1::2] # only odd elements. Even elements are irrelevant 
    hold_dict['image_urls'] = [s['src'] for s in imgs]
    if soup.find('figcaption'):
        hold_dict['image_captions'] = [c.text for c in soup.findAll('figcaption')]
    else:
        hold_dict['image_captions'] = []       
    return(hold_dict)


   
def parse_champion(html):
    '''
    CHAMPION NIGERIA. site_url = "http://www.championnews.com.ng/sitemap_index.xml"
    example url: "http://www.championnews.com.ng/inec-speaks-possibility-postponing-elections/"
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class': 'entry-title'}).text
    hold_dict['date'] = soup.find('time', {'class':re.compile(r'entry-date')}).text
    body = soup.article.find_all('p')
    pars = [par.text for par in body]  
    if soup.find(class_=re.compile(r'caption')):
        hold_dict['image_captions'] = soup.find(class_=re.compile(r'caption')).text 
        pars = [par.split('\n') for par in pars if par != hold_dict['image_captions']]
        pars = sum(pars,[])
    else:
         hold_dict['image_captions'] = []
    if pars[0].split(' ')[0].isupper():
        hold_dict['author'] = pars[0].split(',')[0]
        hold_dict['paragraphs'] = [par.split('\n') for par in pars if hold_dict['author'] not in par]
    else:
        hold_dict['author'] = []
        hold_dict['paragraphs'] = [par.split('\n') for par in pars]
    if not hold_dict['paragraphs']:
        hold_dict['paragraphs'] = pars
    hold_dict['image_urls'] = []
    if soup.article.find('img', {'class':'entry-thumb'}):
        hold_dict['image_urls'] = soup.article.find('img', {'class':'entry-thumb'})['src']
    return(hold_dict)
   
    


def parse_tribune(html):
    '''
    TRIBUNE NIGERIA. site_url = "https://www.tribuneonlineng.com/sitemap_index.xml"
    example url: https://www.tribuneonlineng.com/172684/
    Body of text should be cleaner at bottom, but the page is really inconsistent 
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find(class_=re.compile(r'post-title')).text     
    hold_dict['authors'] = soup.find(class_=re.compile(r'author')).text.strip().replace("By ", "").split(' -')[0]    
    hold_dict['date'] = soup.time.find('b').text
    article_body = soup.find('article').find_all('p')
    pars = [paragraph.text.strip() for paragraph in article_body]   
    hold_dict['paragraphs'] = [p.replace('\xa0', '') for p in pars if p is not '']
    if soup.article.find_all('img'):
        names = [i['data-src'] for i in soup.article.find_all('img')]
        hold_dict['image_urls'] = list(set(names))
        captions = soup.find_all(class_=re.compile(r'caption'))
        captions = list(set([c.text.strip() for c in captions]))
        hold_dict['image_captions'] = [c for c in captions if c is not '']
    else: 
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []
    return(hold_dict)
    



def parse_sahararep(html):
    '''
    SAHARA REPORTERS NIGERIA. site_url = "http://saharareporters.com/sitemap.xml"
    example url: http://saharareporters.com/2006/10/22/fayose-lagos-plot-return-him-power-thickens
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('title').text.strip().split(' By')[0].split('|')[0].split('-')[0].encode('ascii', 'ignore').decode()
    author = soup.find('span', {'class':re.compile(r'attribution')}).text.replace("By ", "").replace("by ", "")
    hold_dict['authors'] = author.encode('ascii', 'ignore').decode() 
    hold_dict['date'] = soup.find('span', {'class':re.compile(r'date')}).text.strip()
    article_body = soup.find('div', {'class':'story-content'})
    pars = [p.text.strip() for p in article_body.find_all('p')]
    hold_dict['paragraphs'] = list(filter(None, pars))
    hold_dict['image_urls'] = [] # No captions in any link I've explored
    if soup.find('div', {'class':'story-content'}).find('img'):
        hold_dict['image_urls'] = soup.find('div', {'class':'story-content'}).find('img')['src']
    hold_dict['image_captions'] = [] 
    if 'Saharareporters' in hold_dict['paragraphs'][0]:
        hold_dict['paragraphs'] = hold_dict['paragraphs'][1:len(hold_dict['paragraphs'])]
    if 'By' in str(hold_dict['paragraphs'][0:2]):     
        pars = hold_dict['paragraphs']
        pos = int(np.where(["By" in s for s in pars[0:2]])[0])
        hold_dict['paragraphs'] = pars[pos+1:len(pars)]
        hold_dict['authors'] += ''.join(", " + pars[pos][3:len(pars[pos])].encode('ascii', 'ignore').decode('utf-8'))
    hold_dict['paragraphs'] = [p.replace(u'\xa0', u' ') for p in hold_dict['paragraphs']]
    return(hold_dict)
         



def parse_sun(html):
    '''
    THE SUN NIGERIA. site_url = "https://www.sunnewsonline.com/sitemap-index-1.xml"
    example url: https://www.sunnewsonline.com/unilag-student-sets-new-record-graduates-with-5-cgpa
    Very hacky, but produces almost no errors. Will update if it becomes problematic.
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class':re.compile(r'title')}).text
    hold_dict['date'] = soup.find('div', {'class':re.compile(r'date')}).text.strip()
    hold_dict['authors'] = soup.find('h3', {'class':re.compile(r'jeg_author_name')}).text.strip()
    article_body = soup.find('div', {'class':'content-inner'})
    pars = [p.text.encode('ascii', 'ignore').decode().split('\n') for p in article_body.find_all('p')]
    hold_dict['paragraphs'] = [y for x in pars for y in x] #flatten list of lists
    hold_dict['image_urls'] = []
    try:
        hold_dict['image_urls'] = soup.find('div', {'class':'jeg_inner_content'}).find('img')['data-src']
    except:
        pass
    hold_dict['image_captions'] = [] # no captions in many links I looked at
    preps = ['From', 'By', 'BY']
    if any([prep in str(hold_dict['paragraphs'][0:4]) for prep in preps]) and len(hold_dict['paragraphs'])>=4:       
        pars = hold_dict['paragraphs'] # just to make code more legible
        pos = np.where([prep in str(s) for s in pars[0:4] for prep in preps])[0][0]
        pos = int(np.where(pos<=2, 0, 
                           (np.where(pos>2 and pos<=5, 1, 
                                     (np.where(pos>5 and pos<=8,2,3))))))
        hold_dict['paragraphs'] = pars[pos+1:len(pars)]
        author = ' '.join(pars[pos].split(" ")[1:3]).replace(',','').replace('-','')
        hold_dict['authors'] += ''.join(', ' + author)
    if 'Source:' in str(hold_dict['paragraphs'][0]) and len(hold_dict['paragraphs'])>2:
        hold_dict['paragraphs'] = hold_dict['paragraphs'][1:len(hold_dict['paragraphs'])]
    return(hold_dict)   
    
















