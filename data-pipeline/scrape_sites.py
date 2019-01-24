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



# Some no years or months, just a sequence:
def xml_gen_seq(num):
    return f'https://www.tribuneonlineng.com/post-sitemap{num}.xml'


## GUARDIAN NIGERIA

# sitemap in site_url = "https://guardian.ng/sitemap.xml"

def parse_guardianng(html):
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
    # First paragraph always hanging without tag. If all text, also caption. 
    # So take all text and remove matched caption on first par only. Hence finding captions first
    body = soup.find('article').text 
    hold_dict['paragraphs'] =  list(filter(None, body.split('\n'))) # getting paragraphs indexed by line breaks; if by 'p', first par is lost. Remove potential empty ones.
    if hold_dict['image_captions']:
        hold_dict['paragraphs'][0] = hold_dict['paragraphs'][0].replace(hold_dict['image_captions'][0], '') #remove caption match
        hold_dict['paragraphs'] = list(filter(None,  hold_dict['paragraphs'])) # Remove empty ones. Important to do this again in case all caption was first par  
    return(hold_dict)


# example url: https://guardian.ng/news/putin-warns-of-consequences-over-orthodox-split/        



## THE PUNCH NIGERIA

# sitemap in: "https://punchng.com/sitemap.xml"
    
def parse_punch(html):
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', class_='post_title').text    
    # Again, location shows up on author string, separated by a comma. So:  
    hold_dict['authors'] = []
    if soup.article.find("strong"):
        hold_dict['authors'] = soup.article.find("strong").text.split(',')[0]
    if "Copyright PUNCH." in hold_dict['authors'] or "READ ALSO" in hold_dict['authors']:
        hold_dict['authors'] = []
    hold_dict['date'] = soup.find('time', class_=re.compile(r'entry-date published')).text   
    pars = [paragraph.text.strip() for paragraph in soup.find('div', class_='entry-content').find_all('p')] # there were some empty paragraphs        
    if len(pars)==0: # means all text in one 'p', sep by '\n' instead
        pars = soup.find('div', class_='col-md-12 col-lg-8').find_all('div')
        pars = [p.text.replace("\n","") for p in pars]  # Best I could do for these rare cases.       
    if hold_dict['authors']:
        if hold_dict['authors'] in pars[0]: ## If author names appear in first paragraph of text, out
            pars = pars[1:len(pars)]
    hold_dict['paragraphs'] =  list(filter(None, pars)) # assign pars and remove empty ones
    # One last refinement to authors: news agencies often appear in last paragraph, catching some at least:
    if ('AFP' or 'Reuters' or 'NAN' or 'AP') in pars[len(pars)-1]:
        hold_dict['authors'] = pars[len(pars)-1].replace('(', '').replace(')', '')
    image_url = soup.find_all('div', class_='blurry')[0]['style']
    hold_dict['image_urls'] = image_url[image_url.find("(")+2:image_url.find(")")-1] # can't split here, have to substring
    hold_dict['image_captions'] = []
    if soup.find('span', class_='caption'):
        hold_dict['image_captions'] = soup.find('span', class_='caption').text              
    return(hold_dict)
    
# example url: https://punchng.com/nigerian-air-force-redeploys-27-air-marshals-45-senior-officers/


    
## VANGUARD NIGERIA

# sitemap in "http://www.vanguardngr.com/sitemap_index.xml"

import numpy as np   
def parse_vanguard(html):
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class': 'entry-title'}).text    
    if soup.find('time', {'class': 'entry-date published'}): # some don't have date
        hold_dict['date'] = soup.find('time', {'class': 'entry-date published'}).text
    else:
        hold_dict['date'] = soup.find('meta', property='article:published_time')['content'].split('T')[0]
            # I don't do this for all because it's GMT and slightly inaccurate
    hold_dict['authors'] = []
    if soup.find('div', id="rtp-author-box"):
        hold_dict['authors'] = soup.find('div', id="rtp-author-box").find('h2').text # Is nested finds an elegant solution? 
            # Sometimes no author
    pars = [p.text for p in soup.find('article').find_all('p') if p.text is not ''] # there were some empty paragraphs
    # If no 'By ' within first  two paragraphs, it's all text. If 'By ', there's author and often subheaders. If 'by' is in small caps, I'm not sure what could be done. 
    if 'By' in str(pars[0:2]):     
        # Remove crap at the top, including author:
        pos = int(np.where(["By" in s for s in pars[0:2]])[0])
        hold_dict['paragraphs'] = pars[pos+1:len(pars)]
        # Extract new author from text:
        hold_dict['authors'] += ''.join(", " + pars[pos][3:len(pars[pos])])
    elif len(pars) is 0: 
        hold_dict['paragraphs'] = soup.find('article').text
    else:   
        hold_dict['paragraphs'] = pars
    #Small bug when ONLY first par is separated by \n but rest by \p. Incredible but true. Fix:
    if '\n' in hold_dict['authors']:
        hold_dict['paragraphs'] = [hold_dict['authors'].split('\n')[1]] + hold_dict['paragraphs']   
        hold_dict['authors'] = hold_dict['authors'].split('\n')[0]
    # Images. When none, no caption. When one or more:
    imgs = soup.article.find_all('img', class_=re.compile(r'size-full'))[1::2] # only odd elements. Even elements are irrelevant 
    hold_dict['image_urls'] = [s['src'] for s in imgs]
    if soup.find('figcaption'):
        hold_dict['image_captions'] = [c.text for c in soup.findAll('figcaption')]
    else:
        hold_dict['image_captions'] = []       
    return(hold_dict)

# example url: https://www.vanguardngr.com/2019/01/video-kwara-apcs-governorship-candidate-abdulrazaq-shuts-down-ilorin/



## CHAMPION NIGERIA
    
# sitemap in: "http://www.championnews.com.ng/sitemap_index.xml"
   
def parse_champion(html):
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class': 'entry-title'}).text
    hold_dict['date'] = soup.find('time', {'class':re.compile(r'entry-date')}).text
    body = soup.article.find_all('p')
    pars = [par.text for par in body]  
    if soup.find(class_=re.compile(r'caption')):
        hold_dict['image_captions'] = soup.find(class_=re.compile(r'caption')).text 
        pars = [par.split('\n') for par in pars if par != hold_dict['image_captions']]
        pars = sum(pars,[]) #unlist one
        #if they exist, image captions are first paragraph, hence odd placement here
    else:
         hold_dict['image_captions'] = []
        # image caption removed if it happens to be first paragraph --rare but needs to be done    
    if pars[0].split(' ')[0].isupper(): # best I could think of is consistency around caps for author names
        hold_dict['author'] = pars[0].split(',')[0] #sometimes city is in there
        hold_dict['paragraphs'] = [par.split('\n') for par in pars if hold_dict['author'] not in par]
    else:
        hold_dict['author'] = []
        hold_dict['paragraphs'] = [par.split('\n') for par in pars]
    if not hold_dict['paragraphs']:
        hold_dict['paragraphs'] = pars
            # have to dump everything at some point, this is already a condition fest
    hold_dict['image_urls'] = []
    if soup.article.find('img', {'class':'entry-thumb'}):
        hold_dict['image_urls'] = soup.article.find('img', {'class':'entry-thumb'})['src']
    return(hold_dict)
   
    
# example url: "http://www.championnews.com.ng/inec-speaks-possibility-postponing-elections/"


## TRIBUNE NIGERIA

# sitemap in: https://www.tribuneonlineng.com/sitemap_index.xml"

def parse_tribune(html):
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
    
# Body of text should be cleaner at bottom, but the page is too inconsistent to find a solid solution
# example url: https://www.tribuneonlineng.com/172684/



## SAHARA REPORTERS

# sitemap in:  "http://saharareporters.com/sitemap.xml"

def parse_sahararep(html):
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('title').text.strip().split(' By')[0].split('|')[0].split('-')[0].encode('ascii', 'ignore').decode()
    # extra info in title can be separated by 'By', '|' or '-'...
    author = soup.find('span', {'class':re.compile(r'attribution')}).text.replace("By ", "").replace("by ", "")
    hold_dict['authors'] = author.encode('ascii', 'ignore').decode() 
    # sometimes unicode carachters creep in both in title and author; strip doesn't remove them
    hold_dict['date'] = soup.find('span', {'class':re.compile(r'date')}).text.strip()
    article_body = soup.find('div', {'class':'story-content'})
    pars = [p.text.strip() for p in article_body.find_all('p')]
    hold_dict['paragraphs'] = list(filter(None, pars))
    hold_dict['image_urls'] = [] # No captions in any link I've explored
    if soup.find('div', {'class':'story-content'}).find('img'):
        hold_dict['image_urls'] = soup.find('div', {'class':'story-content'}).find('img')['src']
    hold_dict['image_captions'] = [] 
    # Other fixes:
    # Sometimes saharareporters in first paragraph of text:
    if 'Saharareporters' in hold_dict['paragraphs'][0]:
        hold_dict['paragraphs'] = hold_dict['paragraphs'][1:len(hold_dict['paragraphs'])]
    # Sometimes author in first/second paragraph of text, even if authorship attributed to 'saharareports'
    if 'By' in str(hold_dict['paragraphs'][0:2]):     
        # Remove crap at the top, including author:
        pars = hold_dict['paragraphs'] # just to make code more legible
        pos = int(np.where(["By" in s for s in pars[0:2]])[0])
        hold_dict['paragraphs'] = pars[pos+1:len(pars)]
        # Extract new author from text:
        hold_dict['authors'] += ''.join(", " + pars[pos][3:len(pars[pos])].encode('ascii', 'ignore').decode('utf-8'))
    # One last replace for paragraphs so it removes unicode crap strip() can't handle. Replace better than encoding here
    hold_dict['paragraphs'] = [p.replace(u'\xa0', u' ') for p in hold_dict['paragraphs']]
    return(hold_dict)
         
# example url: http://saharareporters.com/2006/10/22/fayose-lagos-plot-return-him-power-thickens


  
    
## THE SUN NIGERIA   
  
# sitemap in: https://www.sunnewsonline.com/sitemap-index-1.xml
    
def parse_sun(html):
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class':re.compile(r'title')}).text
    hold_dict['date'] = soup.find('div', {'class':re.compile(r'date')}).text.strip()
    # Author really varies, but take author box now and then try append one in a 'p'
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
    # Other fixes:
    # Author often in pars 1 or 2, starting with words 'from' or 'by'
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
    # Sometimes first line is source, need to remove:
    if 'Source:' in str(hold_dict['paragraphs'][0]) and len(hold_dict['paragraphs'])>2:
        hold_dict['paragraphs'] = hold_dict['paragraphs'][1:len(hold_dict['paragraphs'])]
    return(hold_dict)   
    
# example url: 'https://www.sunnewsonline.com/unilag-student-sets-new-record-graduates-with-5-cgpa



