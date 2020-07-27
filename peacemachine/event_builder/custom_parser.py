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
                'date_publish': {'$type': 'null'},
                'source_domain': domain[:-1]
            }
        )
        missingTextCount = db.articles.count_documents(
            {
                'maintext': {'$type': 'null'},
                'source_domain': domain[:-1]
            }
        )
        missingTitleCount = db.articles.count_documents(
            {
                'title': {'$type': 'null'},
                'source_domain': domain[:-1]
            }
        )
        hold_dict[domain[:-1]] = {"date_publish": missingDateCount, "maintext": missingTextCount, "title": missingTitleCount}

    return hold_dict
    
#%%
missing_data = checkForMissingValues('../../../domains/domains_Uganda.txt')


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
        date = article_date.find('a').text
        hold_dict['date'] = dateparser.parse(date)
    except: 
        article_date = None
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

#%%    
def extraec_story(soup):
    """
    Function to pull the information we want from Extra.ec stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find_all('p', attrs={"class": "paragraph"})
        maintext = [para.text for para in article_body]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def eluniversocom_story(soup):
    """
    Function to pull the information we want from Eluniverso.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"id": "content", "class": "column"})
        body = article_body.find('div', attrs={"class": "field-name-body"})
        maintext = [para.text for para in body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"id": "content", "class": "column"})
        date = article_date.find('span', attrs={"class": "field-content"}).text.split("-")[0]
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict
      
#%%
def elcomerciocom_story(soup):
    """
    Function to pull the information we want from Elcomercio.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "paragraphs"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "date"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

# %%
def eltelegrafocom_story(soup):
    """
    Function to pull the information we want from Eltelegrafo.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "entry-content clearfix"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class": "entry-meta-date updated"})
        date = article_date.a.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def lahoracomec_story(soup):
    """
    Function to pull the information we want from Lahora.com.ec stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "row contentArticulo"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "headerArticulo"})
        date = article_date.h3.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('div', attrs={"class": "headerArticulo"})
        hold_dict['title'] = article_title.h1.text
    except:
        article_title = None
    return hold_dict

# %%  
def expresoec_story(soup):
    """
    Function to pull the information we want from Expreso.ec stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "content-modules-container"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def diarioqueec_story(soup):
    """
    Function to pull the information we want from Diarioque.ec stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "small-12 columns content"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    return hold_dict
    
#%%
def eltiempocom_story(soup):
    """
    Function to pull the information we want from Eltiempo.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        maintext = [para.text for para in soup.find_all('p', attrs={"class": "contenido"})]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class": "fecha"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def lagacetacomec_story(soup):
    """
    Function to pull the information we want from Lagaceta.com.ec stories
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
        article_date = soup.find('time', attrs={"class": "entry-date updated td-module-date"})
        date = article_date['datetime']
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None   
    #title
    try:
        article_title = soup.find('h1', attrs={"class":"entry-title"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict
    
#%%
def elnorteec_story(soup):
    """
    Function to pull the information we want from Elnorte.ec stories
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
    return hold_dict

#%%
def gazetaexpresscom_story(soup):
    """
    Function to pull the information we want from Gazetaexpress.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "single__content"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def kosovapresscom_story(soup):
    """
    Function to pull the information we want from Kosovapress.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "entry-content"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class": "date meta-item"})
        date = article_date.text
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
def kohanet_story(soup):
    """
    Function to pull the information we want from Koha.net stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "news-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        maintext.pop()
        hold_dict['maintext'] = '\n '.join(maintext).strip()
        
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time')
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1')
        hold_dict['title'] = article_title.text.strip(u'\u200b')
    except:
        article_title = None
    return hold_dict

#%%
def botasotinfo_story(soup):
    """
    Function to pull the information we want from Botasot.info stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "paragraph-holder"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class":"img-auth"})
        date = article_date.span.text
        date = " ".join(date[date.find("Më"):].split(" ")[1:4])
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

#%%
def epokaerecom_story(soup):
    """
    Function to pull the information we want from Epokaere.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('main', attrs={"class": "article__main"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "datetime_holder"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def kosovasotinfo_story(soup):
    """
    Function to pull the information we want from Kosova-sot.info stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "news-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        maintext.pop(0)
        maintext.pop()
        hold_dict['maintext'] = '\n '.join(maintext).strip()
        
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('ul', attrs={"class": "published-info"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date= None
    #title
    try:
        article_title = soup.find('h1', attrs={"class":"main-title"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict
    
#%%
def malijetcom_story(soup):
    """
    Function to pull the information we want from Malijet.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"id": "article_body"})
        maintext = [para.text.strip() for para in article_body.find_all('p')][:-1]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class": "story_date"})
        date = article_date.text.split(":")[1].strip()
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class":"page_title"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict
    
#%%
def lecalameinfo_story(soup):
    """
    Function to pull the information we want from Lecalame.info stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "field field-name-body field-type-text-with-summary field-label-hidden"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class": "date"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date= None
    #title
    try:
        article_title = soup.find('div', attrs={"id":"title"})
        hold_dict['title'] = article_title.h2.text
    except:
        article_title = None
    return hold_dict
    
#%%
def alwiaminfo_story(soup):
    """
    Function to pull the information we want from Alwiam.info stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "field field-name-body field-type-text-with-summary field-label-hidden"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class": "date"})
        date = article_date.text.split(",")[1].strip()
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_title = None
    #title
    try:
        article_title = soup.find('div', attrs={"id":"title"})
        hold_dict['title'] = article_title.h1.text
    except:
        article_title = None
    return hold_dict
    
#%%
def frzahraamr_story(soup):
    """
    Function to pull the information we want from Fr.zahraa.mr stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "field field-name-body field-type-text-with-summary field-label-hidden"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class":"title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict
    pass

#%%
def lematinma_story(soup):
    """
    Function to pull the information we want from Lematin.ma stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"itemprop": "articleBody"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time')
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"id":"title"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict

#%%
def almaghribiama_story(soup):
    """
    Function to pull the information we want from Lematin.ma stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "article"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "time"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('div', attrs={"class":"sec-info"})
        hold_dict['title'] = article_title.h1.text
    except:
        article_title = None
    return hold_dict

#%%
#this method returns different format output instead of Arabic
def marocpresscom_story(soup):
    """
    Function to pull the information we want from Marocpress.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "post_content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #title
    try:
        article_title = soup.find('h3')
        hold_dict['title'] = article_title.a['title']
    except:
        article_title = None
    return hold_dict

#%%
def alakhbarpressma_story(soup):
    """
    Function to pull the information we want from Marocpress.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "entry-content entry clearfix"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class":"date meta-item fa-before"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "post-title entry-title"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict
   
#%%
#returns different format output
def assabahma_story(soup):
    """
    Function to pull the information we want from Assabah.ma stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "entry-content entry clearfix"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class":"date meta-item fa-before"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "post-title entry-title"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict

#%%
def leconomistecom_story(soup):
    """
    Function to pull the information we want from Leconomiste.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = [para.text.strip() for para in soup.find_all('p', attrs={"class": "rtejustify"})]
        hold_dict['maintext'] = '\n '.join(article_body).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class":"author"})
        date = article_date.text.split("|")[1].strip().split(" ")[-1]
        hold_dict['date'] = dateparser.parse(date, date_formats=['%d/%m/%Y'])
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('div', attrs={"id": "content_leconomiste"})
        hold_dict['title'] = article_title.h1.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def aminiyadailytrustcomng_story(soup):
    """
    Function to pull the information we want from Aminiya.dailytrust.com.ng stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('article', attrs={"class": "article_content__2HqGP"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class":"article_headline__yVgYO"})
        date = article_date.find('div', attrs={"class":"article_date__33NGW"})
        date = date.div.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def businessnewscomng_story(soup):
    """
    Function to pull the information we want from Businessnews.com.ng stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"id": "content-area"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"id":"post-info"})
        date = article_date.text[article_date.text.find("on")+2:].strip()
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "headline"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict
    
#%%
def sunnewsonlinecom_story(soup):
    """
    Function to pull the information we want from Sunnewsonline.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "content-inner"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class":"jeg_meta_date"})
        date = article_date.text.replace("th","").strip()
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "jeg_post_title"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict
    
#%%
def guardianng_story(soup):
    """
    Function to pull the information we want from Guardian.ng stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "single-article-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class":"manual-age single-article-datetime"})
        date = article_date.text.strip().split("|")[0]
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def nationaldailyngcom_story(soup):
    """
    Function to pull the information we want from Nationaldailyng.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "td-post-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
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
def punchngcom_story(soup):
    """
    Function to pull the information we want from Punchng.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "entry-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')][:-3]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time', attrs={"class": "entry-date published"})
        date = article_date['datetime']
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def vanguardngrcom_story(soup):
    """
    Function to pull the information we want from Vanguardngr.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "entry-title"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict

#%%
def abccompy_story(soup):
    """
    Function to pull the information we want from Abc.com.py stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "article-intro"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "article-date"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def paraguaycom_story(soup):
    """
    Function to pull the information we want from Paraguay.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "news_story"})
        maintext = [para.text.strip() for para in article_body.find_all('div')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('p', attrs={"class": "news_category_and_date"})
        date = article_date.text.split("|")[0].strip()
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('div', attrs={"class": "interior_main_column"})
        hold_dict['title'] = article_title.h1.text
    except:
        article_title = None
    return hold_dict
    
#%%
def hoycompy_story(soup):
    """
    Function to pull the information we want from Hoy.com.py stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "entry-text"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('p', attrs={"class": "byline"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "h-b--lg push-bottom-sm"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def adndigitalcompy_story(soup):
    """
    Function to pull the information we want from Adndigital.com.py stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "entry"})
        unwanted = article_body.find('section', attrs={"id": "related_posts"})
        unwanted.extract()
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def lesoleilsn_story(soup):
    """
    Function to pull the information we want from Lesoleil.sn stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "simple-text size-4 tt-content title-droid margin-big"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class":"tt-post-date-single"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "c-h1"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict

#%%
def xalimasncom_story(soup):
    """
    Function to pull the information we want from Xalimasn.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "td-post-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time', attrs={"class":"entry-date updated td-module-date"})
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
def walfgroupecom_story(soup):
    """
    Function to pull the information we want from Walf-groupe.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "single-posts-wrapper"})
        body = article_body.find('div', attrs ={"class": "entry-content"})
        maintext = [para.text.strip() for para in body.find_all('p')]
        maintext.pop()
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time', attrs={"class":"entry-date published updated"})
        date = article_date['datetime']
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def dakaractucom_story(soup):
    """
    Function to pull the information we want from Dakaractu.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "texte"})
        hold_dict['maintext'] = article_body.text.strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"id":"date"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict
    
#%%
def ausenegalcom_story(soup):
    """
    Function to pull the information we want from Au-senegal.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "texte surlignable clearfix"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('abbr', attrs={"class":"published"})
        date = article_date['title']
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "surlignable"})
        hold_dict['title'] = article_title.text
    except:
        article_title = None
    return hold_dict

#%%
def thecitizencotz_story(soup):
    """
    Function to pull the information we want from Thecitizen.co.tz stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('section', attrs={"class": "body-copy"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def dailynewscotz_story(soup):
    """
    Function to pull the information we want from Dailynews.co.tz stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "entry-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "post-meta-date"})
        date = article_date.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h4', attrs={"class": "title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def ippmediacom_story(soup):
    """
    Function to pull the information we want from Ippmedia.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "field field-name-body field-type-text-with-summary field-label-hidden"})
        body = article_body.find('div', attrs={"class": "field-item even"})
        maintext = [para.text.strip() for para in body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def monitorcoug_story(soup):
    """
    Function to pull the information we want from Monitor.co.ug stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('section', attrs={"class": "body-copy"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class":"story-view"})
        date = article_date.h6.text
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict
    
#%%
def chimpreportscom_story(soup):
    """
    Function to pull the information we want from Chimpreports.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "entry-content entry clearfix"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def newvisioncoug_story(soup):
    """
    Function to pull the information we want from Newvision.co.ug stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "article-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "publish-date"})
        article_date = article_date.text.strip().split(" ")[1:]
        date = " ".join(article_date)
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def bukeddecoug_story(soup):
    """
    Function to pull the information we want from Bukedde.co.ug stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "article-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def observerug_story(soup):
    """
    Function to pull the information we want from Observer.ug stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('span', attrs={"itemprop": "articleBody"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time', attrs={"itemprop": "datePublished"})
        date = article_date['datetime']
        hold_dict['date'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"itemprop": "name"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict
#%%  
header = {
        'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36'
        '(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')
        }

url = 'https://observer.ug/news/headlines/65836-ethiopia-fuels-regional-tensions-with-nile-river-mega-dam'
response = requests.get(url, headers=header).text
soup = BeautifulSoup(response)

# %%  
text= observerug_story(soup)

#%%
def getUrlforDomain(domain):
    urls = db.articles.count_documents(
        {
            'source_domain': domain
        }
    )
    return urls

urls = getUrlforDomain("ferloo.com")

#%%
missing_urls = [i['url'] for i in db.articles.find(
        {
            'source_domain': 'observer.ug',
            '$or': [{'maintext': None}, {'title': None}, {'date_publish':None}]
        }
    )]



# %%
