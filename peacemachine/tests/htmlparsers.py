# TODO: Fix the style for the story functions

import re
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser

# try this first 
def np3k(html):
    article = Article('')
    article.set_html(html)
    article.parse()
    # do the title
    title = article.title 
    if '|' in title:
        title = title.split('|')[0]
    # to the text
    text = article.text
    text = text.split('\n')
    text = [p.strip() for p in text if len(p.strip()) > 0]

    return {
            'title': title,
            'authors': article.authors,
            'date_publish': article.publish_date,
            'maintext': text
            }


# ------------------------------------------------------------------------------
# Advocacy
# ------------------------------------------------------------------------------


def cpjorg_story(soup):
    hold_dict = {}
    header = soup.find('div', {'class':'cpj--module--content'})
    hold_dict['title'] = header.find('h1').text.strip()
    hold_dict['date_publish'] = dateparser.parse(header.find('p').text)
    paras = soup.find('article').text
    # split on the new lines
    paras = paras.split('\n\n')
    # now get rid of the new lines
    paras = [re.sub(r'(\n+\s+|\n+)', '', st) for st in paras]
    # TODO: figure out whether to use the abstract or the text
    # TODO: looks like I'll have to use both.... 
    paras = [p.strip() for p in paras]
    paras = [p for p in paras if len(p) > 0]
    # deal with the intro link
    if paras[0].startswith('Click here to read more'):
        paras[1] = paras[0].split(' ')[-1] + ' ' + paras[1]
        del paras[0]
    hold_dict['maintext'] = paras
    return hold_dict


def rsforg_story(soup):
    hold_dict = {}
    hold_dict['title'] = soup.find('h1', {'class': re.compile(
                                        'content-page__title')}).text.strip()
    hold_dict['date_publish'] = dateparser.parse(soup.find('span',
                         {'property': 'dc:date dc:created'})['content'])
    hold_dict['abstract'] = soup.find('section', {
                            'class': 'content-page__chapo'}).text.strip()
    paras = soup.find('section', {
                        'class': re.compile('content-page__body')}).find_all('p')
    paras = [p.text for p in paras if len(p.text) > 0]
    hold_dict['maintext'] = paras
    return hold_dict


def amnestyorg_story(soup):
    # https://www.amnesty.org/en/latest/news/2016/10/nigeria-tens-of-thousands-of-residents-of-waterfront-communities-at-risk-of-imminent-mass-forced-evictions-in-lagos/
    hold_dict = {}
    hold_dict['title'] = soup.find('h1', {'class':re.compile('heading--main')}).text.strip()
    hold_dict['date_publish'] = dateparser.parse(soup.find('time')['datetime'])
    paras = soup.find('div', {'class':'wysiwyg'}).find_all('p')
    hold_dict['maintext'] = [p.text.strip() for p in paras]
    return hold_dict


def freedomhouseorg_story(soup):
    # https://freedomhouse.org/article/tajikistan-government-must-cease-retaliation-against-activists-exercising-freedom-speech
    hold_dict = {}
    hold_dict['title'] = soup.find('h1', {'class':'title'}).text.strip()
    hold_dict['date_publish'] = dateparser.parse(soup.find('div', {'class':re.compile('field field-name-post-date')}).text)
    paras = soup.find('div', {'class':re.compile('field field-name-body')}).find_all('p')
    paras = [p.text.strip() for p in paras if len(p.text.strip()) > 0]
    hold_dict['maintext'] = paras
    return hold_dict


def netblocksorg_story(soup):
    # https://netblocks.org/reports/facebook-twitter-instagram-whatsapp-and-other-social-media-blocked-in-algeria-eBOgJxBZ
    hold_dict = {}
    hold_dict['title'] = soup.find('h1', {'class':'entry-title'}).text.strip()
    hold_dict['date_publish'] = dateparser.parse(soup.find('time', {'class':'entry-date published'})['datetime'])
    paras = soup.find('div', {'class':'entry-content'}).find_all('p')
    paras = [p.text.strip() for p in paras if len(p.text.strip()) > 0]
    hold_dict['maintext'] = paras
    return hold_dict


# -------------
# International
# -------------

def reuterscom_story(soup):
    """
    Function to pull the information we want from Retuers stories
    """
    # create a dictionary to hold everything in
    hold_dict = {}
    # first turn the html into BeautifulSoup
    # pull the data I want
    # all the initial data I want is in the header so I restrict my search
        # so as to not accidentially pull in other  data
    header = header = soup.find('div', {'class':'ArticleHeader_container'})
    # title
    try:
        hold_dict['title'] = header.find('h1', {
            'class': 'ArticleHeader_headline'}).text
    except: 
        hold_dict['title'] = ''
    # authors
    try:
        authors = header.find('div', {'class': 'BylineBar_byline'})
        hold_dict['authors'] = [author.text for author in authors.find_all('a')]
    except:
        hold_dict['authors'] = ''
    # date
    try:
        hold_dict['date_publish'] = header.find('div', {
            'class': 'ArticleHeader_date'}).text
    except:
        hold_dict['date_publish'] = ''
    # section
    try:
        hold_dict['section'] = [header.find('div', {
            'class': 'ArticleHeader_channel'}).text]
    except:
        hold_dict['section'] = []
    # text
    body = soup.find('div', {'class': 'StandardArticleBody_body'})
    text = [paragraph.text.strip() for paragraph in body.find_all('p')
            if not paragraph.has_attr('class')]
    if text[0].startswith('(') and text[0].endswith(')'):
        del text[0]
    hold_dict['maintext'] = text
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]
    
    # images (in order)
    try:
        image_containers = body.find_all('div', {'class': 'Image_container'})
        images = [image.find('div', {'class': re.compile('LazyImage_image')})
                  for image in image_containers]
        hold_dict['image_urls'] = [re.search(r'\((.*?)\)',
                                   image['style']).group(1) for
                                   image in images]
        # captions (in order)
        hold_dict['image_captions'] = [image.find('div', {
                                       'class': 'Image_caption'}).text
                                       for image in image_containers]
    except AttributeError:
        hold_dict['image_urls'] = []
        # captions (in order)
        hold_dict['image_captions'] = []
    # return
    return hold_dict


def ap_story(path):
    hold_arts = []
    with open(path, encoding='utf-8') as f:
        exf = f.read()
    soup = BeautifulSoup(exf, 'lxml')
    articles = soup.find_all('div', {'id': re.compile('article-')})
    for art in articles:
        hold_dict = {}
        hold_dict['title'] = art.find('span',
                                      {'class': 'enHeadline'}).text.strip()
        divs = art.find_all('div', {'class': None})
        for div in divs:
            if div.text == 'AP Photostream':
                continue
            try:
                hold_dict['date_publish'] = dateparser.parse(div.text)
                break
            except:
                pass
        paragraphs = art.find_all('p', 
                                  {'class': re.compile('articleParagraph')})
        if len(paragraphs) > 0:
            paragraphs = [p.text for p in paragraphs]
            hold_dict['maintext'] = paragraphs
            hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]
        else:
            continue
        hold_arts.append(hold_dict)
    return hold_arts


def nytimescom_story(soup):
    """
    Function to pull the information we want from NYT stories

    Keyword arguments:
    html -- locallay saved or pre-downloaded html
    """
    # create a dictionary to hold everything in
    hold_dict = {}
    # first turn the html into BeautifulSoup
    # pull the data I want
    # all the initial data I want is in the header so I restrict my search
        # so as to not accidentially pull in other  data
    header = soup.find('article').find('header')
    # title
    hold_dict['title'] = header.find('h1', itemprop='headline').text
    # authors
    try:
        authors_html = header.find('p', itemprop='author creator')
        hold_dict['authors'] = [tag.text for tag in authors_html.find_all('span', itemprop='name')]
    except:
        hold_dict['authors'] = []
    # date
    try:
        hold_dict['date_publish'] = header.find('time')['datetime']
    except: 
        hold_dict['date_publish'] = ''
    # text
    try:
        article_body = soup.find('section', itemprop='articleBody')
        hold_dict['maintext'] = [paragraph.text for paragraph in article_body.find_all('p')]
    except AttributeError:
        article_body = soup.find_all('p', {'class':'story-body-text story-content'})
        hold_dict['maintext'] = [paragraph.text.strip() for paragraph in article_body]
        hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]
    try:
        # images (in order)
            # beautifulsoup has a had time with the data-testid so I used an alternate way to search
        images = soup.find_all('div', {'data-testid':'photoviewer-wrapper'})
        hold_dict['image_urls'] = [image.find('img')['src'] for image in images]
        # captions (in order)
        hold_dict['image_captions'] = [image.find('figcaption', itemprop='caption description').text for image in images]
    except:
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []
    # return
    return(hold_dict)


def aljazeeracom_story(soup):
    #create a dictionary to hold everything in
    hold_dict = {}
    #get title
    try:
        title_box = soup.find('h1', attrs={'class':'post-title'})
        hold_dict['title'] = title_box.text.strip() #strip() is used to remove starting and trailing
    except:
        hold_dict['title'] = ''
    #get the authors. not all articles have authors, especially wire reports.
    try:
        hold_dict['authors'] = list(set([a.text.strip() for a in soup.find_all('a', attrs={'rel':'author'})]))
    except: 
        hold_dict['authors'] = ''
    #get the date.
    date_box = soup.find('div', attrs={'class':'article-duration'})
    hold_dict['date_publish'] = date_box.text.strip()

    #get section
    try:
        section_box = soup.find('li', attrs={'id':'articlestoptopic'})
        hold_dict['section'] = [section_box.text.strip()]
    except: 
        hold_dict['section'] = []

    #get the text.
    text_box = soup.find('div', attrs={'class':'article-p-wrapper'})
    hold_dict['maintext'] = [p.text.strip() for p in text_box.find_all('p')]
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]
    #get the article first paragraph
    abstract_box = soup.find('p', attrs={'class':'article-heading-des'})
    hold_dict['abstract'] = abstract_box.text.strip()

    #no reported location for this publication.
    try: 
        #get the source
        source_box = soup.find('div', attrs={'class':'article-body-artSource'})

        #get the images
        image_box = soup.find_all('img',attrs={'class':re.compile('img-responsive')})
        hold_dict['image_urls'] = [i['src'] for i in image_box]

        #get the captions
        caption_box = soup.find_all('figcaption', attrs={'class':'main-article-caption'})
        hold_dict['image_captions'] = [caption.text.strip() for caption in caption_box]
    except:
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []

    return hold_dict


def theguardiancom_story(soup):
    #create a dictionary to hold everything in
    hold_dict = {}

    # req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
    # html = urllib.request.urlopen(req).read()

    #get title
    title_box = soup.find('h1', attrs={'class':'content__headline'})
    hold_dict['title'] = title_box.text.strip() #strip() is used to remove starting and trailing

    #get the authors. not all articles have authors, especially wire reports.
    try:
        hold_dict['authors'] = list(set([a.text.strip() for a in soup.find_all('span', attrs={'itemprop':'name'})]))
    except:
        hold_dict['authors'] = []

    #get the date.
    date_box = soup.find('time', attrs={'class':re.compile('content__dateline')})
    hold_dict['date_publish'] = date_box.text.strip()

    #get section
    try:
        section_box = soup.find('span', attrs={'class':'label__link-wrapper'})
        hold_dict['section'] = [section_box.text.strip()]
    except:
        hold_dict['section'] = []

    #get the text.
    text_box = soup.find('div', attrs={'class':re.compile('content__article-body')})
    hold_dict['maintext'] = [p.text.strip() for p in text_box.find_all('p')]
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]

    #get the article first paragraph
    try:
        abstract_box = soup.find('div', attrs={'class':'content__standfirst'})
        hold_dict['abstract'] = abstract_box.text.strip()
    except:
        hold_dict['abstract'] = ''

    #no reported location for this publication.
    try:
        #get the images
        image_box = soup.find_all('img',attrs={'class':'gu-image'})
        hold_dict['image_urls'] = [i['src'] for i in image_box]

        #get the captions
        caption_box = soup.find_all('figcaption', attrs={'class':re.compile('caption')})
        hold_dict['image_captions'] = [caption.text.strip() for caption in caption_box]
    except:
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []

    return hold_dict


def washingtonpostcom_story(url):

    #url = 'https://www.washingtonpost.com/local/immigration/getting-through-the-border-fence-was-easy-winning-the-right-to-stay-wont-be/2019/01/17/980ec59a-03ce-11e9-b5df-5d3874f1ac36_story.html?utm_term=.494b209cecdd'

    #create a dictionary to hold everything in
    hold_dict = {}

    req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
    html = urllib.request.urlopen(req).read()

    #get title
    title_box = soup.find('h1', attrs={'data-pb-field':'custom.topperDisplayName'})
    hold_dict['title'] = title_box.text.strip() #strip() is used to remove starting and trailing

    #get the authors
    try:
        hold_dict['authors'] = list(set([a.text.strip() for a in soup.find_all('a', attrs={'class':'author-name'})]))
    except:
        hold_dict['authors'] = []

    #get the date.
    date_box = soup.find('span', attrs={'itemprop':'datePublished'})
    hold_dict['date_publish'] = date_box.text.strip()

    #get section
    try:
        section_box = soup.find('a', attrs={'class':'kicker-link'})
        hold_dict['section'] = [section_box.text.strip()]
    except:
        hold_dict['section'] = []

    #get the article first paragraph
    try:
        abstract_box = soup.find('p', attrs={'data-elm-loc':'1'})
        hold_dict['abstract'] = abstract_box.text.strip()
    except:
        hold_dict['abstract'] = ''

    #get the text
    text_box = soup.find('article', attrs={'itemprop':'articleBody'})
    hold_dict['maintext'] = [p.text.strip() for p in text_box.find_all('p')]
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]

    #get the images
    try:
        image_box = [x.find('img',attrs={'class':'unprocessed'}) for x in soup.find_all('div',attrs={'class':re.compile('inline-content')}) if x.find('img',attrs={'class':'unprocessed'})]
        hold_dict['image_urls'] = [i['data-hi-res-src'] for i in image_box]
    except:
        hold_dict['image_urls'] = []

    #get the captions
    try:
        caption_box = soup.find_all('span', attrs={'class':re.compile('pb-caption')})
        hold_dict['image_captions'] = [caption.text.strip() for caption in caption_box]
    except:
        hold_dict['image_captions'] = []

    return hold_dict


def bloombergcom_story(soup):

    """
    get the story data for bloomberg stories

    note: still missing the gen and collect functions for Bloomberg because 
    of their stringent html download policies
    
    #url = 'https://www.bloomberg.com/news/articles/2019-01-18/trump-to-hold-second-summit-with-north-korea-s-kim-in-february'
    #url = 'https://www.bloomberg.com/news/articles/2019-01-30/boeing-cracks-100-billion-sales-mark-sees-new-gains-in-2019?srnd=premium'    
    """

    #create a dictionary to hold everything in
    hold_dict = {}


    #get title
    hold_dict['title'] = soup.find('h1', attrs={'class':'lede-text-v2__hed'}).text.strip()

    #get the authors. not all articles have authors, especially wire reports.
    try:
        hold_dict['authors'] = list(set([a.text.strip() for a in soup.find_all('a', attrs={'class':'author-v2__byline'})]))
    except:
        hold_dict['authors'] = []

    #get the publish date.
    hold_dict['date_publish'] = soup.find('time', attrs={'class':'article-timestamp'}).find('noscript').text.strip()

    #get section
    try:
        hold_dict['section'] = soup.find('div', attrs={'class':'eyebrow-v2'}).text.strip()
    except:
        hold_dict['section'] = []

    #get the text.
    text_box = soup.find('div', attrs={'class':'body-copy-v2 fence-body'})
    hold_dict['maintext'] = [p.text.strip() for p in text_box.find_all('p')]
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]

    #get the article first paragraph
    try:
        abstract_box = soup.find('ul', attrs={'class':'abstract_v2'})
        hold_dict['abstract'] = [x.child.text.strip() for x in abstract_box] if soup.find('ul', attrs={'class':'abstract_v2'}) else [p.text.strip() for p in text_box.find_all('p')][0]
    except:
        hold_dict['abstract'] = []

    try:
        #get the images
        hold_dict['image_urls'] = [x['src'] for x in soup.find_all('img',attrs={'class':re.compile('lazy-img__image')})]
        #get the captions
        caption_box1 = soup.find_all('div', attrs={'class':'news-figure-caption-text caption'})
        caption_box2 = soup.find_all('span', attrs={'class':re.compile('lede-small-image-v2__caption')})
        hold_dict['image_captions'] = [x.text.strip() for x in caption_box1] if caption_box1 != [] else [x.text.strip() for x in caption_box2]
    except:
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []

    return hold_dict


def dwcom_story(soup):
    """get story data for dw urls. """
    #url = 'https://www.dw.com/en/obasanjo-disputed-elections-are-better-than-no-elections/a-47181718'
    #url = 'https://www.dw.com/en/uk-pm-theresa-may-to-take-brexit-options-back-to-eu-negotiators/a-47170783'

    #create a dictionary to hold everything in
    hold_dict = {}

    #req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
    #html = urllib.request.urlopen(req).read()

    #get title
    hold_dict['title'] = soup.find('h1').text.strip()

    #get the authors. not all articles have authors, especially wire reports.
    smallList = soup.find('ul', {'class':'smallList'})

    try:
        hold_dict['author'] = smallList.find(text='Author').parent.next_sibling.strip().split(',')
    except:
        hold_dict['author'] = []

    #get the date. format dd.mm.yyyy
    hold_dict['date_publish'] = smallList.find(text='date_publish').parent.next_sibling.strip().split(',')

    #get section
    try:
        hold_dict['section'] =[ soup.find('h4', attrs={'class':'artikel'}).text.strip()]
    except:
        hold_dict['section'] = []

    #get the text.
    text_box = soup.find('div', attrs={'class':'longText'})
    hold_dict['maintext'] = [p.text.strip() for p in text_box.find_all('p')]
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]

    #get the article first paragraph
    try:
        hold_dict['abstract'] = soup.find('p', attrs={'class':'intro'}).text.strip()
    except:
        hold_dict['abstract'] = []

    #get the images
    try:
        image_box = [x for x in soup.find_all('a', attrs={'class':re.compile('overlayLink')}) if str(x).find('img') > 0]
        rest2 = [str(x).split('<img')[1] for x in image_box]
        srcs = [str(x).split('src="')[1] for x in rest2]
        hold_dict['image_urls'] = [str(x).split('" title=')[0] for x in srcs]

        #get the captions
        rest3 = [str(x).split('alt="')[1] for x in image_box]
        hold_dict['image_captions'] = [str(x).split('" ')[0] for x in rest3]
    except:
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []

    return hold_dict


def france24com_story(soup):
    
    hold_dict = {}


    #get title
    hold_dict['title'] = soup.find('h1', attrs={'class':re.compile('t-content__title')}).text.strip()

    #get the authors. not all articles have authors, especially wire reports.
    hold_dict['author'] = str(set([x.text.strip() for x in soup.find_all('span',attrs={'class':'m-from-author__name'})]))

    #get the date. format dd.mm.yyyy
    date_box = [x.text.strip() for x in soup.find_all('span',attrs={'class':'m-pub-dates__date'})]
    hold_dict['date_publish'] = date_box[0]

    #get section
    try:
        hold_dict['section'] = [soup.find('a', attrs={'class':'m-breadcrumb__list__item__link'}).text.strip()]
    except:
        hold_dict['section'] = []

    #get the text.
    text_box = soup.find('div', attrs={'class':'t-content__body'})
    hold_dict['maintext'] = [p.text.strip() for p in text_box.find_all('p')]
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]

    #get the article first paragraph
    try:
        hold_dict['abstract'] = soup.find('p', attrs={'class':'t-content__chapo'}).text.strip()
    except:
        hold_dict['abstract'] = []

    return hold_dict


# ------------
# Kenya
# ------------
def nationnet_story(soup):
    #create a dictionary to hold everything in
    hold_dict = {}


    article_box = soup.find('article', attrs={'class':'article'})

    #get title
    hold_dict['title'] = soup.find('h2').text.strip()

    #get the authors. not all articles have authors
    try:
        author_box = article_box.find('section', attrs={'class':'author noprint'})
        hold_dict['author'] = [x.text.strip() for x in author_box.find_all('strong')]
    except:
        hold_dict['author'] = []

    #get the date. format dd.mmm.yyyy
    hold_dict['date_publish'] = soup.find('h6',).text.strip()

    #get section(s)
    try:
        hold_dict['section'] = [x.text.strip().split('\n')[-1] for x in soup.find_all('ol', attrs={'class':'breadcrumb'})]
    except:
        hold_dict['section'] = []

    #get the text.
    hold_dict['maintext'] = [p.text.strip() for p in article_box.find_all('p')]
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]

    #get the article first paragraph
    try:
        abstract_box = article_box.find('section',attrs={'class':'summary'})
        hold_dict['abstract'] = [p.text.strip() for p in abstract_box.find_all('li')]
    except:
        hold_dict['abstract'] = []

    #reported location.
    try:
        hold_dict['location'] = article_box.find('p', attrs={'class':'MsoNormal'}).text.strip()
    except:
        hold_dict['location'] = ''

    try:
        #get the images
        hold_dict['image_urls'] = [x['src'] for x in soup.find_all('img', attrs={'class':'photo_article'})]
        #get the captions
        hold_dict['image_captions'] = [x.text.strip() for x in soup.find_all('p', attrs={'id':'photo_article_caption'})]
    except:
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []

    return hold_dict


def theeastafricancoke_story(soup):
    """
    collecting story data for theeastafrican.
    the sitemap seems to be out of date here, but allegedly resides at the
    following link: https://www.theeastafrican.co.ke/sitemap/sitemap-index.xml

    #url = 'https://www.theeastafrican.co.ke/news/ea/3-suspected-Ugandans-held-over-terrorism-Mozambique/4552908-4957298-jar2fez/index.html'
    #url = 'https://www.theeastafrican.co.ke/business/Kenyans-protest-Tanzania-unfair-trade-practices/2560-4956968-tdboud/index.html'
    """

    #create a dictionary to hold everything in
    hold_dict = {}

    # req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
    # html = urllib.request.urlopen(req).read()

    article_box = soup.find('article', attrs={'class':'article'})

    #get title
    hold_dict['title'] = soup.find('h2').text.strip()

    #get the authors. not all articles have authors
    try:
        author_box = article_box.find('section', attrs={'class':'author noprint'})
        hold_dict['author'] = [x.text.strip() for x in author_box.find_all('strong')]
    except:
        hold_dict['author'] = []

    #get the date. format dd.mmm.yyyy
    hold_dict['date_publish'] = soup.find('h6',).text.strip()

    #get section(s)
    try:
        hold_dict['section'] = [x.text.strip().split('\n')[-1] for x in soup.find_all('ol', attrs={'class':'breadcrumb'})]
    except:
        hold_dict['section'] = []

    #get the text.
    hold_dict['maintext'] = [p.text.strip() for p in article_box.find_all('p')]
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]

    #get the article first paragraph
    try:
        abstract_box = article_box.find('section',attrs={'class':'summary'})
        hold_dict['abstract'] = [p.text.strip() for p in abstract_box.find_all('li')]
    except:
        hold_dict['abstract'] = []

    try:
        #get the images
        hold_dict['image_urls'] = [x['src'] for x in soup.find_all('img', attrs={'class':'photo_article'})]
        #get the captions
        hold_dict['image_captions'] = [x.text.strip() for x in soup.find_all('p', attrs={'id':'photo_article_caption'})]
    except:
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []

    return hold_dict


def ksnmediacom_story(soup):
    #create a dictionary to hold everything in
    hold_dict = {}

    #req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
    #html = urllib.request.urlopen(req).read()

    article_box = soup.find('div', attrs={'id':'mvp-content-main'})

    #get title
    hold_dict['title'] = soup.find('h1').text.strip()

    #get the authors. not all articles have authors
    try:
        hold_dict['author'] = [x.text.strip() for x in soup.find('span', attrs={'class':re.compile('author-name')}).find_all('a')]
    except:
        hold_dict['author'] = []

    #get the date. format dd.mmm.yyyy
    hold_dict['date_publish'] = soup.find('span',attrs={'class':'mvp-post-date updated'}).text.strip()

    #get section(s)
    try:
        hold_dict['section'] = list(set([x.text.strip() for x in soup.find_all('span', attrs={'class':'mvp-post-cat left'})]))
    except:
        hold_dict['section'] = []

    #get the text.
    hold_dict['maintext'] = [p.text.strip() for p in article_box.find_all('p')]
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]

    #get the article first paragraph
    try:
        hold_dict['abstract'] = [p.text.strip() for p in article_box.find_all('p')][0]
    except:
        hold_dict['abstract'] = []

    try:
        #get the images
        hold_dict['image_urls'] = [x.parent.find('article').find('img')['src'] for x in article_box.find_all('figcaption')] + [x.find('img')['src'] for x in soup.find_all('div',attrs={'id':'mvp-post-feat-img'})] + [x['src'] for x in article_box.find_all('img',attrs={'class':re.compile('size-full')})]
        #get the captions
        hold_dict['image_captions'] = [x.text.strip() for x in article_box.find_all('figcaption')] + [x.text.strip() for x in article_box.find_all('p', attrs={'class':'wp-caption-text'})]
    except:
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []

    return hold_dict


def kbccoke_story(soup):
    hold_dict = {}    
    hold_dict['title'] = soup.find('h1', {'class': 'entry-title'}).text
    author_box = soup.find('div', {'class':'td-post-small-box'})
    if author_box:
        hold_dict['authors'] = author_box.find('a').text
    else:
        hold_dict['authors'] = []
    hold_dict['date_publish'] = soup.find('time', {'class':'entry-date updated td-module-date'})['datetime'].split('T')[0]
    body = soup.find('div', {'class':'td-post-content'}).find_all('p') 
    pars = [paragraph.text.encode('ascii', 'ignore').decode() for paragraph in body]
    hold_dict['maintext'] = list(filter(None, pars))    
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]
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


def citizentvcoke_story(soup):
    '''
    Citizen Kenya. Sitemap: "https://citizentv.co.ke/sitemap_index.xml"
    url = "https://citizentv.co.ke/sports/plane-cushions-found-in-search-for-footballer-sala-229191/"
    '''
    hold_dict = {}    
    hold_dict['title'] = soup.find('h1', {'class': 'articleh1'}).text
    try:
        hold_dict['authors'] = soup.find('span', {'itemprop':'name'}).text
    except:
        hold_dict['authors'] = []
    hold_dict['date_publish'] = " ".join(soup.find('span', {'class':'date-tag'}).text.split(" ")[0:3])
    body = soup.find('span', {'itemprop':'description'}).find_all('p', recursive=False) 
    pars = [paragraph.text.encode('ascii', 'ignore').decode() for paragraph in body][:-1]
    hold_dict['maintext'] = list(filter(None, pars))
    
    try:
        img = [i.find('img') for i in soup.find_all("figure")] 
        hold_dict['image_urls'] = [img[0]['src']]
        if len(img) > 1:
            hold_dict['image_urls'].append([i['data-lazy-src'] for i in img[1:]])

        captions = [i.find('figcaption') for i in soup.find_all("figure")]
        hold_dict['image_captions'] = [c.text.strip() for c in captions]
    
    except:
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []
 
    return(hold_dict)


def the_starcoke(soup):
    hold_dict={}
    try:
        header=soup.find('div', {'class':'l-region l-region--title'})
        hold_dict['title']=header.find('div', {'class':'pane-content'}).text.strip()
        header_auth=soup.find('div', {'class':'panel-pane pane-entity-field pane-node-field-converge-byline'})
        hold_dict['authors']=header_auth.find('div', {'class':'field__item even'}).text[3:].split(' and ')
        header_section=soup.find('div',{'class':'panel-pane pane-block pane-crumbs-breadcrumb'})
        hold_dict['section']=header_section.find('a',{'href':'/sections/national-news_c29654'}).text
    except AttributeError:
        hold_dict['title'] = soup.find('h1', {'class':re.compile('article-title')}).text.strip()

    try:
        hold_dict['date_publish']=header.find('div', {'class':'field__item even'}).text
    except:
        hold_dict['date_publish'] = dateparser.parse(soup.find('div', {'class':'article-published'}).text.strip())

    try:
        body=soup.find('div', {'class':'field field-name-body'})
        hold_dict['maintext'] = [paragraph.text.strip() for paragraph in body.find_all('p')][:-1]
        hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]
    except AttributeError:
        body=soup.find('div', {'class':'maintext'})
        hold_dict['maintext'] = [paragraph.text.strip() for paragraph in body.find_all('p')][:-1]
        hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]
        
    img_cont = soup.find('div', {'class':'panel-pane pane-entity-field pane-node-field-converge-image'})
    if img_cont:
        hold_dict['image'] = [img['src'] for img in img_cont.find_all('img')]
    else:
        hold_dict['image'] = []
    if img_cont:
        hold_dict['caption'] = [img['alt'] for img in img_cont.find_all('img')]
    else:
        hold_dict['caption'] = []
    return hold_dict


def citizentvcoke_story(soup):
    '''
    url = 'https://citizentv.co.ke/news/wambora-governor-with-9-lives-says-impeachment-attempts-have-taught-him-resilience-229263/'
    '''
    hold_dict = {}
    hold_dict['title'] = soup.find('h1', {'class': 'articleh1'}).text
    try:
        hold_dict['authors'] = soup.find('span', {'itemprop':'name'}).text
    except:
        hold_dict['authors'] = []
    hold_dict['date_publish'] = " ".join(soup.find('span', {'class':'date-tag'}).text.split(" ")[0:3])
    body = soup.find('span', {'itemprop':'description'}).find_all('p', recursive=False)
    pars = [paragraph.text.encode('ascii', 'ignore').decode() for paragraph in body][:-1]
    hold_dict['maintext'] = list(filter(None, pars))
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


def standardmediacoke_story(soup):
    """
    url='https://www.standardmedia.co.ke/article/2001306089/raila-hosts-uhuru-in-first-kisumu-visit-since-handshake'
    """
    hold_dict={}
    hold_dict['title'] = soup.find('h1', {'class':'article-title'}).text.strip()
    try:
        hold_dict['date_publish'] = soup.find('li', {'style':'font-size: 10px'}).text.strip().split('Posted on: ')[1].split(' GMT')[0]
    except:
        date = [str(ii).strip() for ii in soup.find('ul', {'class':'article-meta'}).find('li') if type(ii) == bs4.element.NavigableString]
        date = [ii for ii in date if len(ii) > 0][0]
        hold_dict['date_publish'] = date
    try:
        hold_dict['authors'] = soup.find('ul', {'class':'article-meta'}).text.strip().split('\n')[0].split(' and ')
    except:
        hold_dict['authors'] = []
    try:
        sec = soup.find('ol',{'class':'breadcrumb'}).text.strip().split('\n')
        hold_dict['section'] = [s for s in sec if s] # careful, previous one returned filter object
    except:
        hold_dict['section'] = []

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
    body = [s.rstrip() for s in body if hold_dict['date_publish'] not in s and hold_dict['authors'][0] not in s \
                                    and hold_dict['title'] not in s and 'SEE ALSO' not in s and 'function()' not in s]
    if hold_dict['caption'][0] is not '':
        body = [s for s in body if hold_dict['caption'][0] not in s]
    hold_dict['maintext'] = list(filter(None, body))
    return hold_dict

# ------------
# Nigeria
# ------------
def guardianng_story(soup):
    '''
    GUARDIAN NIGERIA. site_url = "https://guardian.ng/sitemap.xml"
    example url: https://guardian.ng/news/putin-warns-of-consequences-over-orthodox-split/        
    '''
    hold_dict = {}    
    try:
        hold_dict['title'] = soup.find('h1', {'class':re.compile(r'after-category')}).text.replace("\xa0", "") 
    except:
        hold_dict['title']
    try:
        author = soup.find('div', {'class':re.compile(r'author')}).text.strip().replace("By ", "")
        hold_dict['authors'] = author.split(',')[0] # remove cities or positions
    except: 
        hold_dict['authors'] = []

    hold_dict['date_publish'] = ' '.join(soup.find('div', {'class':re.compile(r'manual-age')}).text.split())


    hold_dict['image_urls'] = []
    hold_dict['image_captions'] = []
    try:
        hold_dict['image_urls'] = [i['src'] for i in soup.article.find_all('img') if '/plugins/' not in i['src']]
        captions = soup.find_all(class_=re.compile(r'caption'))
        hold_dict['image_captions'] = list(set([c.text.strip() for c in captions]))
    except:
        pass
    try:
        body = soup.find('article').text 
        hold_dict['maintext'] =  list(filter(None, body.split('\n'))) # getting paragraphs indexed by line breaks; if by 'p', first par is lost. Remove potential empty ones.
        if hold_dict['image_captions']:
            hold_dict['maintext'][0] = hold_dict['maintext'][0].replace(hold_dict['image_captions'][0], '') #remove caption match
            hold_dict['maintext'] = list(filter(None,  hold_dict['maintext'])) # Remove empty ones. Important to do this again in case all caption was first par  
    except:
        hold_dict['maintext'] = []
    return(hold_dict)


def punchngcom_story(soup):
    '''
    PUNCH NIGERIA. site_url = "https://punchng.com/sitemap.xml"
    example url: https://punchng.com/nigerian-air-force-redeploys-27-air-marshals-45-senior-officers/
    '''
    hold_dict = {}    
    hold_dict['title'] = soup.find('h1', {'class':'post_title'}).text
    hold_dict['authors'] = []
    if soup.article.find("strong"):
        hold_dict['authors'] = soup.article.find("strong").text.split(',')[0]
    if "Copyright PUNCH." in hold_dict['authors'] or "READ ALSO" in hold_dict['authors']:
        hold_dict['authors'] = []
    hold_dict['date_publish'] = soup.find('time', {'class': re.compile(r'entry-date published')}).text   
    pars = [paragraph.text.strip() for paragraph in soup.find('div', {'class':'entry-content'}).find_all('p')] # there were some empty paragraphs        
    if len(pars)==0: 
        pars = soup.find('div', class_='col-md-12 col-lg-8').find_all('div')
        pars = [p.text.replace("\n","") for p in pars]  
    if hold_dict['authors']:
        if hold_dict['authors'] in pars[0]:
            pars = pars[1:len(pars)]
    hold_dict['maintext'] =  list(filter(None, pars)) # assign pars and remove empty ones
    if ('AFP' or 'Reuters' or 'NAN' or 'AP') in pars[len(pars)-1]:
        hold_dict['authors'] = pars[len(pars)-1].replace('(', '').replace(')', '')
    try:
        image_url = soup.find_all('div', class_='blurry')[0]['style']
        hold_dict['image_urls'] = image_url[image_url.find("(")+2:image_url.find(")")-1] # can't split here, have to substring
        hold_dict['image_captions'] = []
        if soup.find('span', {'class':'caption'}):
            hold_dict['image_captions'] = soup.find('span', {'class':'caption'}).text        
    except:
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []

    return hold_dict


def vanguardngrcom_story(soup):
    hold_dict = {}    
    hold_dict['title'] = soup.find('h1', {'class': 'entry-title'}).text    
    if soup.find('time', {'class': 'entry-date published'}): # some don't have date
        hold_dict['date_publish'] = soup.find('time', {'class': 'entry-date published'}).text
    else:
        hold_dict['date_publish'] = soup.find('meta', property='article:published_time')['content'].split('T')[0]
    hold_dict['authors'] = []
    if soup.find('div', id="rtp-author-box"):
        hold_dict['authors'] = soup.find('div', id="rtp-author-box").find('h2').text # Is nested finds an elegant solution? 
    pars = [p.text.strip() for p in soup.find('article').find_all('p') if p.text is not ''] # there were some empty paragraphs
    if len(pars) is 0: 
        hold_dict['maintext'] = [soup.find('article').text]
    else:
        for ii in [0,1]:
            if pars[ii].startswith('By'):
                hold_dict['authors'] = pars[ii]
                del pars[ii]
        hold_dict['maintext'] = [pars]
    # if '\n' in hold_dict['authors']:
    #     hold_dict['maintext'] = [hold_dict['authors'].split('\n')[1]] + hold_dict['maintext']   
    #     hold_dict['authors'] = hold_dict['authors'].split('\n')[0]
    try:
        imgs = soup.article.find_all('img', class_=re.compile(r'size-full'))[1::2] # only odd elements. Even elements are irrelevant 
        hold_dict['image_urls'] = [s['src'] for s in imgs]
        if soup.find('figcaption'):
            hold_dict['image_captions'] = [c.text for c in soup.findAll('figcaption')]
        else:
            hold_dict['image_captions'] = []
    except:
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []

    return(hold_dict)


def championnewscomng_story(soup):
    hold_dict = {}    
    hold_dict['title'] = soup.find('h1', {'class': 'entry-title'}).text
    hold_dict['date_publish'] = soup.find('time', {'class':re.compile(r'entry-date')}).text
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
        hold_dict['maintext'] = [par.split('\n') for par in pars if hold_dict['author'] not in par]
    else:
        hold_dict['author'] = []
        hold_dict['maintext'] = [par.split('\n') for par in pars]
    if not hold_dict['maintext']:
        hold_dict['maintext'] = pars
    hold_dict['maintext'] = [p.strip() for p in hold_dict['maintext'] if len(p.strip()) > 0]
    hold_dict['image_urls'] = []
    if soup.article.find('img', {'class':'entry-thumb'}):
        hold_dict['image_urls'] = soup.article.find('img', {'class':'entry-thumb'})['src']
    return(hold_dict)
   

def tribuneonlineng_story(soup):
    hold_dict = {}    
    hold_dict['title'] = soup.find(class_=re.compile(r'post-title')).text 
    try:    
        hold_dict['authors'] = soup.find(class_=re.compile(r'author')).text.strip().replace("By ", "").split(' -')[0]    
    except:
        hold_dict['authors'] = []
    hold_dict['date_publish'] = soup.time.find('b').text
    article_body = soup.find('article').find_all('p')
    pars = [paragraph.text.strip() for paragraph in article_body]   
    hold_dict['maintext'] = [p.replace('\xa0', '') for p in pars if p is not '']
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]
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


def saharareporterscom_story(soup):
    '''
    SAHARA REPORTERS NIGERIA. site_url = "http://saharareporters.com/sitemap.xml"
    example url: http://saharareporters.com/2006/10/22/fayose-lagos-plot-return-him-power-thickens
    '''
    hold_dict = {}    
    hold_dict['title'] = soup.find('title').text.strip().split(' By')[0].split('|')[0].split('-')[0].encode('ascii', 'ignore').decode()
    try:
        author = soup.find('span', {'class':re.compile(r'attribution')}).text.replace("By ", "").replace("by ", "")
        hold_dict['authors'] = author.encode('ascii', 'ignore').decode()
    except:
        hold_dict['authors'] = []

    hold_dict['date_publish'] = soup.find('span', {'class':re.compile(r'date_publish')}).text.strip()
    article_body = soup.find('div', {'class':'story-content'})
    pars = [p.text.strip() for p in article_body.find_all('p')]
    hold_dict['maintext'] = list(filter(None, pars))
    hold_dict['image_urls'] = [] # No captions in any link I've explored
    if soup.find('div', {'class':'story-content'}).find('img'):
        hold_dict['image_urls'] = soup.find('div', {'class':'story-content'}).find('img')['src']
    hold_dict['image_captions'] = [] 
    if 'Saharareporters' in hold_dict['maintext'][0]:
        hold_dict['maintext'] = hold_dict['maintext'][1:len(hold_dict['maintext'])]
    if 'By' in str(hold_dict['maintext'][0:2]):     
        pars = hold_dict['maintext']
        pos = int(np.where(["By" in s for s in pars[0:2]])[0])
        hold_dict['maintext'] = pars[pos+1:len(pars)]
        hold_dict['authors'] += ''.join(", " + pars[pos][3:len(pars[pos])].encode('ascii', 'ignore').decode('utf-8'))
    hold_dict['maintext'] = [p.replace(u'\xa0', u' ') for p in hold_dict['maintext']]
    return(hold_dict)


def sunnewsonlinecom_story(soup):
    hold_dict = {}    
    hold_dict['title'] = soup.find('h1', {'class':re.compile(r'title')}).text
    hold_dict['date_publish'] = soup.find('div', {'class':re.compile(r'date_publish')}).text.strip()
    try:
        hold_dict['authors'] = soup.find('h3', {'class':re.compile(r'jeg_author_name')}).text.strip()
    except: 
        hold_dict['authors'] = ''
    
    article_body = soup.find('div', {'class':'content-inner'})
    pars = [p.text.encode('ascii', 'ignore').decode().split('\n') for p in article_body.find_all('p')]
    hold_dict['maintext'] = [y for x in pars for y in x] #flatten list of lists
    hold_dict['image_urls'] = []
    try:
        hold_dict['image_urls'] = soup.find('div', {'class':'jeg_inner_content'}).find('img')['data-src']
    except:
        pass
    hold_dict['image_captions'] = [] # no captions in many links I looked at
    preps = ['From', 'By', 'BY']
    if any([prep in str(hold_dict['maintext'][0:4]) for prep in preps]) and len(hold_dict['maintext'])>=4:       
        pars = hold_dict['maintext'] # just to make code more legible
        pos = np.where([prep in str(s) for s in pars[0:4] for prep in preps])[0][0]
        pos = int(np.where(pos<=2, 0, 
                           (np.where(pos>2 and pos<=5, 1, 
                                     (np.where(pos>5 and pos<=8,2,3))))))
        hold_dict['maintext'] = pars[pos+1:len(pars)]
        author = ' '.join(pars[pos].split(" ")[1:3]).replace(',','').replace('-','')
        hold_dict['authors'] += ''.join(', ' + author)
    if 'Source:' in str(hold_dict['maintext'][0]) and len(hold_dict['maintext'])>2:
        hold_dict['maintext'] = hold_dict['maintext'][1:len(hold_dict['maintext'])]
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]
    return(hold_dict)  


def nationaldailyngcom_story(soup):
    """
    There is no information for the sitemap when using https://www.nan.ng/robots.txt
    Section is messy, when multiple section couldn't divide them
    Images have no captions
    url = 'http://nationaldailyng.com/code-of-conduct-tribunal-vs-saraki-free-speech-and-politics-of-contempt/'
    """
    hold_dict = {}
    header = soup.find('div', {'class':'td-post-header'})
    hold_dict['title'] = header.find('h1', {'class':'entry-title'}).text.strip()
    hold_dict['date_publish'] = header.find('div', {'class':'td-post-date'}).text
    try:
        hold_dict['authors'] = header.find('div',{'class':'td-post-author-name'}).text.strip().split('By')[1].split('-')[0]
    except:
        hold_dict['authors'] = []
    hold_dict['section'] = header.find('ul', {'class':'td-category'}).text
    picture = soup.find('div',{'class':'td-post-featured-image'})
    if soup.find('div', {'class':'td-post-featured-image'}):
        hold_dict['images'] = [img['src'] for img in picture.find_all('img')]
    body = soup.find('div',{'class':'td-post-content'}).find_all('p')
    pars = [p.text.strip() for p in body]
    pars = [p.split('\n') for p in pars]
    pars = [i for list in body for i in list]
    if len(pars) > 0:
        if re.match(r'(by|from)', pars[0].text, re.I):
            string = re.match(r'(by|from)', pars[0].text, re.I)
            hold_dict['authors'] = pars[0].text[string.span()[1]+1:]
    hold_dict['maintext'] = [p.replace('\n', '') for p in pars if type(p) is bs4.element.NavigableString]
    hold_dict['maintext'] = [p.strip() for p in hold_dict['maintext'] if len(p.strip()) > 0]
    return hold_dict


def nanng_story(soup):
    """
    There is no information for the sitemap when using https://www.nan.ng/robots.txt
    Caption info is messy
    url_1 = 'https://www.nan.ng/news/jonathan-visited-buhari/'
    """
    hold_dict={}
    # header=soup.find('div', {'class':'td-post-header'})
    hold_dict['title']=soup.find('h1', {'itemprop':'headline'}).text.strip()
    hold_dict['date_publish']=soup.find('time', {'itemprop':'datePublished'})['datetime']
    body=soup.find('div',{'itemprop':'articleBody'}).find_all('p')
    firstline = body[0].text
    if firstline.startswith('By'):
        hold_dict['authors'] = firstline.split('By')[1].split('/')
        hold_dict['maintext'] = [p.text.encode('ascii', 'ignore').decode() for p in body if not p.has_attr('class')][1:]
    else:
        hold_dict['authors'] = ['']
        hold_dict['maintext'] = [p.text.encode('ascii', 'ignore').decode() for p in body if not p.has_attr('class')][0:]
    hold_dict['maintext'] = [p.strip() for p in hold_dict['maintext'] if len(p.strip()) > 0]
    return hold_dict

# ------------
# Tanzania
# ------------

def dailynewscotz_story(soup):
    """
    There is no caption for the pictures or section
    There is no information for the sitemap when using https://www.dailynews.co.tz/robots.txt
    If the images are broken the image link is empty
    url = 'https://www.dailynews.co.tz/news/kisutu-court-acquits-tbc1-presenter-jerry-muro.aspx'
    """
    hold_dict={}
    hold_dict['title'] = soup.find('div',{'class':re.compile('title')}).text.strip()
    date = soup.find('div', {'class':'post-meta-date'})
    if date:
        date = date.text.strip()
        hold_dict['date_publish'] = str(datetime.strptime(date, '%d/%m/%Y'))
    try:
        firstline = soup.find('div',{'class':'post-meta-author'}).text.strip()
        if firstline.startswith('By'):
            hold_dict['authors'] = soup.find('div',{'class':'post-meta-author'}).text.strip().split('By ')[1]
        else:
            if firstline.startswith('From'):
                hold_dict['authors'] = soup.find('div',{'class':'post-meta-author'}).text.strip().split('From ')[1].split('in')[0]
            else:
                hold_dict['authors'] = firstline
    except:
        hold_dict['authors'] = []
    try:
        mainpic = soup.find('div',{'class':'entry-media'})
        hold_dict['images'] = [img['src'] for img in mainpic.find_all('img')]
    except:
        hold_dict['images'] = []
    body = soup.find('div', {'class':'entry-content'})
    text = [paragraph.text for paragraph in body.find_all('p')]
    # pars = [p.strip().encode('ascii', 'ignore').decode() for p in text if type(p) is bs4.element.NavigableString]
    hold_dict['maintext'] = list(filter(None, text))
    return hold_dict


def thecitizencotz_story(soup):
        '''
        The code below rarely misses author information if the author information does not follow by @ (see the code below).
        It captured everytime I tried except once where the author's name did not follow by @.
        I just saw it once and it was in entertainment section. All the news in the news section has author
        format like this: "by xxx @xxx". When it is in this format (almost 99%), it works fine. Hence, it is not a big deal.
        Some news pieces had no author or image, that's why I used try and except structure in order not to get error.
        News text start with location information, most of the time Dar es Salaam but it changes especially in international news. I also get
        rid of "related to: [link]" paragraphs which are at the end of the text. I wrote the code in a way that gets rid of any paragraph that
        starts with "related to:". If there is a better way, let me know (like getting rid of any paragraph that contains link etc.)
        url= "https://www.thecitizen.co.tz/News/Study--More-civic-space-required-for-Tanzanians-to-enjoy/1840340-4951430-xtyu6u/index.html"
        '''
        # create a dictionary to hold everything in
        hold_dict = {}
        # first turn the html into BeautifulSoup

        # pull the data I want
        if bool(soup.find('article', {'class':'main column'})):
            header = soup.find('article', {'class':'main column'}).find('header')
            if bool(header.find('h1', {'itemprop':'headline name'})):
                hold_dict['title'] = header.find('h1', {'itemprop':'headline name'}).text.strip()
            else:
                hold_dict['title'] = header.find('h2').text
            if bool(header.find('h6')):
                hold_dict['date_publish'] = header.find('h6').text
            else:
                hold_dict['date_publish'] = header.find('h5').text
        else:
            header = soup.find('div', {'class':'heading'})
            hold_dict['title'] = header.find('h1').text
            hold_dict['date_publish'] = str(soup.find('meta', {'property':'article:published_time'})['content'])

        hold_dict['date_publish'] = dateparser.parse(hold_dict['date_publish'])
        # date Day of the week/Month/Day of the month/Year
        #Author: The author information has the following pattern: "By Serkant @Serkant's Twitter".
        try:
            author = soup.find('section', {'class':'author'}).text
            author = re.search('By(.*) @', author)
            hold_dict['author'] = author.group(1)
        except AttributeError:
            hold_dict['author'] = [""]
        # Section: News seems to be the major category and the rest is entertainment, magazines etc.
        try:
            section = soup.find('ol', {"class": "breadcrumb"}).text
            section_info = section.split()
            hold_dict['section'] = section_info[-1]
        except AttributeError:
            hold_dict['section'] = ''
        
        # text
        if bool(soup.find('section', {'class':'body-copy'})):
            body = soup.find('section', {'class':'body-copy'})

            if bool(body.find('p', {'class':'p1'})):
                text = [paragraph.text for paragraph in body.find_all('p', {'class':'p1'})]    
            else:
                text = [paragraph.text for paragraph in body.find_all('p') if not paragraph.has_attr('class')]
            # removing \xa0 s which are at the end mostly.
            text = [ii.replace("\xa0", "") for ii in text]
            # Getting rid of related to news which are at the end.
            text = [item for item in text if not (item.startswith('Related to:'))]
            # Get rid of the byline 
            first = text[0]
            if first.startswith('By '):
                text[0] = first.split('.')[1].strip()
                try:
                    hold_dict['location'] = first.split('.')[0].split('Reporter')[1]
                except:
                    hold_dict['location'] = ''
            else:
                if '.' in first[:20]:
                    hold_dict['location'] = first.split('.')[0]
                    text[0] = first.split('.')[1].strip()
            text = [ii for ii in text if len(ii) > 0]
            hold_dict['maintext'] = text
        else:
            text = soup.find_all('p', {'class':'p1'})
            hold_dict['maintext'] = [p.text for p in text]

        # images
        try:
            images = soup.find('img', {'class':'photo_article'})["src"]
            link = "thecitizen.co.tz"
            hold_dict['image_urls']= link + images
        except TypeError:
            hold_dict['image_urls'] = [""]
        # image captions
        try:
            hold_dict['image_captions'] = soup.find('p', {'id':'photo_article_caption'}).text
        except AttributeError:
            hold_dict['image_captions'] = [""]
        # return
        return hold_dict


# ippmediacom
# mtanzaniacotz
# def mtanzaniacotz(soup):
#     hold_dict = {}
#     hold_dict['title'] = soup.find('h1', {'class':'entry-title'}).text
#     hold_dict['date_publish'] = dateparser.parse(soup.find('time')['datetime'])
#     text = 

#     return hold_dict


# ------------
# Mali
# ------------
def malijetcom_story(soup):

    #sampleurl: http://malijet.com/les_faits_divers_au_mali/221481-bamako-des-hommes-arm%C3%A9s-cambriolent-la-station-%26amp%3Bquot%3Bbaraka-.html
    
    #create a dictionary to hold everything in
    hold_dict = {}


    #get title
    title_box = soup.find('h1', attrs={'class':'page_title'})
    hold_dict['title'] = title_box.text.strip() #strip() is used to remove starting and trailing

    #get the authors
    try:
        authors_box = soup.find('span', attrs={'class':'story_author'})
        hold_dict['authors'] = authors_box.text.strip()
    except:
        hold_dict['authors'] = []

    #get the date. note: weird format.
    date_box = soup.find('span', attrs={'class':'story_date'})
    hold_dict['date_publish'] = date_box.text.strip()

    #get section. get more specific here
    try:
        section_box = soup.find('div', attrs={'class':'box_breadcrumb'})
        hold_dict['section'] = [section_box.find_all('a')[-1].text.strip()]
    except:
        hold_dict['section'] = []

    #get the article abstract
    try:
        abstract_box = soup.find('p', attrs={'class':'article_abstract'})
        hold_dict['abstract'] = abstract_box.text.strip()
    except:
        hold_dict['abstract'] = ''

    #get the text.
    text_box = soup.find('div', attrs={'id':'article_body'})
    hold_dict['maintext'] = [paragraph.text.strip() for paragraph in text_box.find_all('p') if not paragraph.has_attr('class')]
    hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]

    #get the images
    try:
        image_box = soup.find_all('img', attrs={'class':'img-responsive img-rounded'})
        hold_dict['image_urls'] = [image['src'] for image in image_box if 'article' in image['src']]
    except:
        hold_dict['image_urls'] = []

    #get the captions
    try:
        caption_box = soup.find_all('span', attrs={'class':'image_caption'})
        hold_dict['image_captions'] = [caption.text for caption in caption_box]
    except:
        hold_dict['image_captions'] = []

    return hold_dict


def essorml_story(soup):
    #create a dictionary to hold everything in
    hold_dict = {}

    #req = urllib.request.Request(url,data=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'})
    #html = urllib.request.urlopen(req).read()

    #get title
    
    try:
        hold_dict['title'] = soup.find('title').text.split(' | ')[0].strip()
    except AttributeError:
        hold_dict['title'] = soup.find('h1', attrs={'class':'entry-title'}).text.strip()

    try:
        #get the authors. not all articles have authors
        hold_dict['author'] = [x for x in soup.find('a', attrs={'itemprop':'author'})]
    except:
        hold_dict['author'] =[]

    #get the date. format dayofweek dd month yyyy
    try:
        hold_dict['date_publish'] = soup.find('time',attrs={'class':re.compile('entry-date')}).text.strip()
    except AttributeError:
        hold_dict['date_publish'] = soup.find('li', {'class':'date_publish'}).text.strip()

    #get section(s)
    try:
        hold_dict['section'] = [x.text.strip() for x in soup.find_all('div', attrs={'class':'vbreadcrumb'})]
    except AttributeError:
        hold_dict['section'] = []

    if bool(soup.find('div', attrs={'class':'entry-content clearfix'})):
        article_box = soup.find('div', attrs={'class':'entry-content clearfix'})
        #get the text.
        hold_dict['maintext'] = [p.text.strip() for p in article_box.find_all('p')]
        hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]

        #get the article first paragraph
        hold_dict['abstract'] = [p.text.strip() for p in article_box.find_all('p')][0]

        #no reported location for this publication.
        try:
            #get the images
            hold_dict['image_urls'] = [x['src'] for x in article_box.find_all('img', attrs={'class':re.compile('wp-image')})]

            #get the captions
            hold_dict['image_captions'] = [x.text.strip() for x in article_box.find_all('figure', attrs={'class':'wp-block-image'})]
        except AttributeError:
            pass

    else:
        article = soup.find('div', {'id':'main'})
        text = [p.text.strip() for p in article.find_all('p')]
        hold_dict['abstract'] = text[0]
        hold_dict['maintext'] = text[1:]
        hold_dict['maintext'] = [t for t in hold_dict['maintext']]
        hold_dict['maintext'] = [p for p in hold_dict['maintext'] if len(p) > 0]
        # first_blank = [num for num, tt in enumerate(hold_dict['maintext']) if len(tt) == 0][0]
        # hold_dict['maintext'] = hold_dict['maintext'][:first_blank]

    return hold_dict


def lessorml_story(soup):
    """
    updated version of essor
    """
    hold_dict = {}

    hold_dict['title'] = soup.find('title').text

    date = soup.find('div', {'class':re.compile('main col')}).find('div', {'class':'post-date'}).text

    date = ' '.join(date.split()[1:])

    hold_dict['date_publish'] = mreplace(date, french_months)

    text = soup.find('div', {'class':'article-content clearfix'}).text    

    hold_dict['maintext'] = [' '.join(text.split())]
    

    return hold_dict


def lessorsite_story(soup):
    """
    updated version of essor
    """
    hold_dict = {}

    hold_dict['title'] = soup.find('title').text

    date = soup.find('div', {'class':re.compile('main col')}).find('div', {'class':'post-date'}).text

    date = ' '.join(date.split()[1:])

    hold_dict['date_publish'] = mreplace(date, french_months)

    text = soup.find('div', {'class':'article-content clearfix'}).text

    hold_dict['maintext'] = [' '.join(text.split())]

    return hold_dict


def panoramacomal_story(soup):
    """
    custom parser for panorama.com.al - just missing pieces
    """
    hold_dict = {}

    hold_dict['date_publish'] = dateparser.parse()
