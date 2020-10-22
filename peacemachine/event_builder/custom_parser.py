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
missing_data = checkForMissingValues('../../../domains/domains_international.txt')


# %%
def kohajonecom_story(soup):
    """
    Function to pull the information we want from Kohajone.com stories
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
        hold_dict['date_publish'] = dateparser.parse(date)
    except: 
        article_date = None
    return hold_dict

#%%
def panoramacomal_story(soup):
    """
    Function to pull the information we want from Panorama.al stories
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
    Function to pull the information we want from Gazetashqiptare.al stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class":"content_right"})
        unwanted = article_body.find('div', attrs={"class": "comment_section block_section"})
        if unwanted: unwanted.extract()
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext)
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class":"news_item__date"})
        date = article_date.text.split("-")[1].strip()
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        hold_dict['title'] = soup.find('h1', attrs={"class": "single_article__title"}).text
    except:
        hold_dict['title'] = ''
    return hold_dict

#%%
def gazetaditaal_story(soup):
    """
    Function to pull the information we want from Gazetadita.al stories
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
def telegrafal_story(soup):
    """
    Function to pull the information we want from Telegraf.al stories
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
def beninwebtvcom_story(soup):
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
def newsacotonoucom_story(soup):
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
        hold_dict['date_publish'] = dateparser.parse(date)
        
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def theeastafricancoke_story(soup):
    """
    Function to pull the information we want from Theeastafrican.co.ke stories
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
    #title
    try:
        article_title = soup.find('article', attrs={"class":"main column"})
        hold_dict['title'] = article_title.h2.text
    except:
        article_title = None
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
        if unwanted: unwanted.extract()
        date = " ".join(content.text.strip().split(" ")[:3])
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        article_body = soup.find('div', attrs={"id": "main-content"})
        maintext = [para.text for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "article_title"})
        date = article_date.p.text.split("|")[1].strip()
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('div', attrs={"class": "article_title"})
        hold_dict['title'] = article_title.h2.text
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
    Function to pull the information we want from Almaghribia.ma stories
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
    Function to pull the information we want from Alakhbar.press.ma stories
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date, date_formats=['%d/%m/%Y'])
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        if unwanted: unwanted.extract()
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def diascompy_story(soup):
    """
    Function to pull the information we want from 5dias.com.py stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #date
    try:
        article_date = soup.find('h3', attrs={"class": "mono-caps-condensed--md -byline"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict
    
#%%
def lanacioncompy_story(soup):
    """
    Function to pull the information we want from Lanacion.com.py stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #date
    try:
        article_date = soup.find('div', attrs={"class": "dt"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
        hold_dict['date_publish'] = dateparser.parse(date)
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
def daykyivua_story(soup):
    """
    Function to pull the information we want from Day.kyiv.ua stories
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
        article_date = soup.find('div', attrs={"class": "node_date"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def interfaxcomua_story(soup):
    """
    Function to pull the information we want from Interfax.com.ua stories
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
        article_date = soup.find('div', attrs={"class": "article-time"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "article-content-title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def kpua_story(soup):
    """
    Function to pull the information we want from Kp.ua stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #date
    try:
        article_date = soup.find('a', attrs={"class": "meta__date"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def pravdacomua_story(soup):
    """
    Function to pull the information we want from Pravda.com.ua stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "post_text"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "post_time"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict
  
#%%
def vestiua_story(soup):
    """
    Function to pull the information we want from Vesti.ua stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "the-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "date"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('div', attrs={"class": "content-head"})
        hold_dict['title'] = article_title.h1.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def wzlvivua_story(soup):
    """
    Function to pull the information we want from Wz.lviv.ua stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('article', attrs={"class": "uk-article"})
        maintext = [para.text.strip() for para in article_body.find_all('div')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class": "uk-text-middle"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "uk-article-title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

###Serbia Domains
#%%
def rsn1infocom_story(soup):
    """
    Function to pull the information we want from Rs.n1info.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"id": "articleContent"})
        maintext= [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time', attrs={"class": "pub-date"})
        date = article_date['datetime']
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "single-article-title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def danasrs_story(soup):
    """
    Function to pull the information we want from Danas.rs stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        unwanted = soup.find('div', attrs={"class": "danas-club"})
        if unwanted: unwanted.extract()
        article_body1 = soup.find('div', attrs={"class": "post-intro-content content"})
        maintext = [para.text.strip() for para in article_body1.find_all('p')]
        article_body2 = soup.find('div', attrs={"class": "post-content content"})
        maintext += [para.text.strip() for para in article_body2.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time')
        date = article_date['datetime']
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "post-title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def insajdernet_story(soup):
    """
    Function to pull the information we want from Insajder.net stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "articleView__text"})
        maintext= [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time', attrs={"class": "articleBadge"})
        date = article_date['datetime']
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "articleView__headline"})
        hold_dict['title'] = article_title.text.strip()
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
        article_body = soup.find('article', attrs={"class": "article"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "datetime_holder"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('article', attrs={"class": "article"})
        hold_dict['title'] = article_title.h1.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def juznevesticom_story(soup):
    """
    Function to pull the information we want from Juznevesti.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "desc_holder cf main--content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('p', attrs={"class": "article--single__date"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "mb10 title title--1"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
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
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('ul', attrs={"class": "published-info"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "main-title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def krikrs_story(soup):
    """
    Function to pull the information we want from Krik.rs stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "the_content_wrapper"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def vremecom_story(soup):
    """
    Function to pull the information we want from Vreme.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"id": "mainContent"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class": "datum"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('div', attrs={"id": "mainContent"})
        hold_dict['title'] = article_title.h3.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def istinomerrs_story(soup):
    """
    Function to pull the information we want from Istinomer.rs stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "postexc clear"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        article_body1 = soup.find('div', attrs={"class": "col-md-12 pcont"})
        maintext += [para.text.strip() for para in article_body1.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class": "datum"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict
    
#%%
def astrars_story(soup):
    """
    Function to pull the information we want from Astra.rs stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "text"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        text = ', '.join(maintext).strip()
        hold_dict['maintext'] = '\n'.join(text.split(",")[1:])
    except:
        article_body = None
    return hold_dict

#%%
def pescaniknet_story(soup):
    """
    Function to pull the information we want from Pescanik.net stories
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
        article_date = soup.find('span', attrs={"class": "asdf-post-date"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "entry-title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def cenzolovkars_story(soup):
    """
    Function to pull the information we want from Cenzolovka.rs stories
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
        article_date = soup.find('time', attrs={"class": "entry-date published"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "entry-title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def timescozm_story(soup):
    """
    Function to pull the information we want from Times.co.zm stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "single-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class": "single-date"})
        date = " ".join(article_date.text.split(" ")[2:5])
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('div', attrs={"class": "widget-magmag-title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def bluradiocom_story(soup):
    """
    Function to pull the information we want from Bluradio.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "contenidoDespliegue ng-binding"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time', attrs={"itemprop": "datePublished"})
        date = article_date['content']
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "titulo ng-binding ng-scope"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def noticiascanalrcncom_story(soup):
    """
    Function to pull the information we want from Noticias.canalrcn.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "sumario"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "fecha"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('div', attrs={"class": "titulo"})
        hold_dict['title'] = article_title.h1.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def lasillarotacom_story(soup):
    """
    Function to pull the information we want from Lasillarota.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"id": "crpler"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #title
    try:
        article_title = soup.find('div', attrs={"class": "titulo-nota"})
        hold_dict['title'] = article_title.h1.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def lasillavaciacom_story(soup):
    """
    Function to pull the information we want from Lasillavacia.com stories
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
        article_date = soup.find('div', attrs={"class": "author author-top"})
        date = article_date.p.text.split("·")[1]
        print(date)
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def elespectadorcom_story(soup):
    """
    Function to pull the information we want from Lasillavacia.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "Article-Content"})
        maintext = [para.text.strip() for para in article_body.find_all('p', attrs={"class": "font--secondary"})]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def portafolioco_story(soup):
    """
    Function to pull the information we want from Portafolio.co stories
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
def canal1comco_story(soup):
    """
    Function to pull the information we want from Canal1.com.co stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "article-container"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('time', attrs={"class": "jsx-3840644288"})
        date = article_date['datetime']
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "jsx-3840644288"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%  
def eluniversalcomco_story(soup):
    """
    Function to pull the information we want from Eluniversal.com.co stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "text small resizable"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('span', attrs={"class": "datefrom small"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "headline"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict
  
#%%
def razonpublicacom_story(soup):
    """
    Function to pull the information we want from Razonpublica.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #date
    try:
        article_date = soup.find('time', attrs={"class": "entry-date published"})
        date = article_date['datetime']
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    return hold_dict

#%%
def caracolcomco_story(soup):
    """
    Function to pull the information we want from Caracol.com.co stories
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
    return hold_dict

#%%
def cuestionpublicacom_story(soup):
    """
    Function to pull the information we want from Cuestionpublica.com stories
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
        article_date = soup.find('time', attrs={"class": "entry-date updated td-module-date"})
        date = article_date['datetime']
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "entry-title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

#%%
def proclamadelcaucacom_story(soup):
    """
    Function to pull the information we want from Proclamadelcauca.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "single-entradaContent"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    return hold_dict

#%%
def laorejarojacom_story(soup):
    """
    Function to pull the information we want from Laorejaroja.com stories
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
    return hold_dict

#%%
def lafmcomco_story(soup):
    """
    Function to pull the information we want from Lafm.com.co stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #text
    try:
        article_body = soup.find('div', attrs={"class": "node-content"})
        maintext = [para.text.strip() for para in article_body.find_all('p')]
        hold_dict['maintext'] = '\n '.join(maintext).strip()
    except:
        article_body = None
    #date
    try:
        article_date = soup.find('div', attrs={"class": "node-date"})
        date = article_date.text
        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
    #title
    try:
        article_title = soup.find('h1', attrs={"class": "node__title"})
        hold_dict['title'] = article_title.text.strip()
    except:
        article_title = None
    return hold_dict

def main():
    
    header = {
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36'	        
            '(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')	  
    }
    # url = 'https://www.theeastafrican.co.ke/business/2560-3114720-8nm6slz/index.html'
    # response = requests.get(url, headers=header).text
    # soup = BeautifulSoup(response)
    # text= theeastafricancoke_story(soup)
    # print(text)