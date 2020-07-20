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
missing_data = checkForMissingValues('../domains/domains_Benin.txt')


# %%
def kohajone_story(soup):
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
    hold_dict['date'] = date
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
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class":"single_meta block_section"})
    except:
        article_date = None
    try:
        date = article_date.find('span').text
    except:
        date = ''
    hold_dict['date'] = date
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
        article_date = soup.find('div', attrs={"class":"a-content"})
    except:
        article_date = None
    try:
        date = article_date.find('span', attrs={"class":"meta"}).text.strip()
    except:
        date = ''
    hold_dict['date'] = date
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
        hold_dict['date'] = date
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
        hold_dict['date'] = date
    except:
        article_date = None
    #title
    article_title = soup.find('h1', attrs={"class": "single-post-title"})
    hold_dict['title'] = article_title.text
    return hold_dict
    
# %%  
header = {
        'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36'
        '(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')
        }

url = 'https://beninwebtv.com/2020/07/sessime-son-acerbe-replique-a-une-internaute-qui-choque-les-fans-photo/'
response = requests.get(url, headers=header).text
soup = BeautifulSoup(response)

# %%  
text= beninwebtv_story(soup)

# %%
