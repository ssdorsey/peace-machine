#%%
from pymongo import MongoClient
import re
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
from pprint import pprint
import os

#%%
db = MongoClient('mongodb://akankshanb:HavanKarenge123@vpn.ssdorsey.com:27017/ml4p').ml4p

#%%
def checkForMissingValues(filename):
    domainfile = open(filename, 'r')
    domains = domainfile.readlines()
    hold_dict = {} # holds all the missing data info
    for domain in domains:
        missingDateCount = db.articles.count_documents(
            {
                'date_publish': None,
                'source_domain': domain[:-1]
            }
        )
        missingTextCount = db.articles.count_documents(
            {
                'maintext': None,
                'source_domain': domain[:-1]
            }
        )
        missingTitleCount = db.articles.count_documents(
            {
                'title': None,
                'source_domain': domain[:-1]
            }
        )
        hold_dict[domain[:-1]] = {"date_publish": missingDateCount, "maintext": missingTextCount, "title": missingTitleCount}

    return hold_dict
    

#%%  
missing_data = checkForMissingValues('../../../domains/domains_Kenya.txt')


# %%
def kohajonecom_story(soup):
    """
    Function to pull the information we want from Kohajone stories
    :param soup: BeautifulSoup object, ready to parse
    """
    # create a dictionary to hold everything in
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class":"content-inner"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except: 
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class":"jeg_meta_date"})
    except: 
        article_date = None
    try:
        date = article_date.find('a').text
    except: 
        date = ''
    hold_dict['date'] = dateparser.parse(date)
    return hold_dict

#%%
def panorama_story(soup):
    """
    Function to pull the information we want from Panorama stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class":"td-post-content td-pb-padding-side"})
    except:
        article_body = None
    maintext = [para.text for para in article_body.find_all('p')]
    hold_dict['maintext'] = '\n '.join(maintext)
    return hold_dict

#%%
def gazetashqiptareal_story(soup):
    """
    Function to pull the information we want from Gazetashqiptareal stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class":"content_right"})
        unwanted = article_body.find('div', attrs={"class": "comment_section block_section"})
        unwanted.extract()
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class":"news_item__date"})
        date = article_date.text.split("-")[1].strip()
        print(date)
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        hold_dict['title'] = soup.find('h1', attrs={"class": "single_article__title"}).text
    except:
        hold_dict['title'] = ''
    return hold_dict

#%%
def gazetadita_story(soup):
    """
    Function to pull the information we want from Gazetadita stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class":"shortcode-content"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    
    #date
    try:
        article_date = soup.find('span', attrs={"class":"meta"})
        date = article_date.text.strip()
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1')
    except:
        article_title = None
    hold_dict['title'] = article_title.text
    return hold_dict
    
#%%
def telegraf_story(soup):
    """
    Function to pull the information we want from Telegraf stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class":"td-post-content"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time')
        date = article_date['datetime']
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
       
    #title
    try:
        article_title = soup.find('h1')
    except:
        article_title = None
    hold_dict['title'] = article_title.text
    return hold_dict
 
#%%
def beninwebtv_story(soup):
    """
    Function to pull the information we want from Beninwebtv stories
    :param soup: BeautifulSoup object, ready to parse
    """ 
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class":"entry-content clearfix single-post-content"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time')
        date = article_date['datetime']
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "single-post-title"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict

# %%  
def newsacotonou_story(soup):
    """
    Function to pull the information we want from News.Acotonou stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('span', attrs={"class": "FullArticleTexte"})
        hold_dict['maintext'] = article_body.text.strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "FontArticleSource"}).text.split("|")[0].split(" ")[2:]
        date = " ".join(article_date)
        hold_dict['date'] = dateparser.parse(date)
        
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "FontArticleMainTitle"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict

# %%
def lanationbenininfo_story(soup):
    """
    Function to pull the information we want from Lanationbenin.info stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "entry-content"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time')
        date = article_date['datetime']
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1')
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict

# %%  
def lanouvelletribuneinfo_story(soup):
    """
    Function to pull the information we want from Lanouvelletribune.info stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "content-inner"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "jeg_post_title"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict

# %%  
def capitalethiopiacom_story(soup):
    """
    Function to pull the information we want from Capitalethiopia.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "td-post-content"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time')
        date = article_date['datetime']
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "entry-title"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict

#%%
#This function is not working properly...
def ethiopianreportercom_story(soup):
    """
    Function to pull the information we want from Ethiopianreporter.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #date
    try:
        article_date = soup.find('span',attrs={"class": "post-created"})
        print(article_date)
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%% 
def ambebige_story(soup):
    """
    Function to pull the information we want from Ambebi.ge stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "article_content"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    return hold_dict

#%%  
def georgiatodayge_story(soup):
    """
    Function to pull the information we want from Georgiatoday.ge stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "news-data"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "news-data"})
        date = article_date.div.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict
    
#%%
def nationcoke_story(soup):
    """
    Function to pull the information we want from Nation.co.ke stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('section', attrs={"class": "body-copy"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    return hold_dict

#%%
def standardmediacoke_story(soup):
    """
    Function to pull the information we want from Standardmedia.co.ke stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "content"})
        maintext = article_body.text.strip()
        hold_dict['maintext'] = maintext
    except:
        article_body = None
    try:
        article_date = soup.find('div', attrs={"class": "icon-bar"})
        content = article_date.find('p')
        unwanted = content.find('span')
        unwanted.extract()
        date = " ".join(content.text.strip().split(" ")[:3])
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def businesstodaycoke_story(soup):
    """
    Function to pull the information we want from Businesstoday.co.ke stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"data-role": "article_content"})
        maintext = [para.text for para in article_body.find_all('p')]
        maintext.pop()
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time', attrs={"class": "entry-date published"})
        date = article_date['datetime']
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None   
    #title
    try:
        article_title = soup.find('span', attrs={"class":"entry-title-primary"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict

#%%
def thestarcoke_story(soup):
    """
    Function to pull the information we want from The-star.co.ke stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "text"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "article-published"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict
    
# %%  
header = {
        'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36'
        '(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')
        }

url = 'https://www.the-star.co.ke/news/2020-07-21-uhuru-maraga-tiff-likely-over-lsk-call-not-to-list-24-in-roll-of-senior-counsel/'
response = requests.get(url, headers=header).text
soup = BeautifulSoup(response)


# %%  
text= thestarcoke_story(soup)

#%%
def getUrlforDomain(domain):
    urls = db.articles.count_documents(
        {
            'source_domain': domain
        }
    )
    return urls

urls = getUrlforDomain("the-star.co.ke")
