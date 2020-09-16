#%%
from pymongo import MongoClient
import re
import bs4
from newspaper import Article
import requests
from pprint import pprint
import os
import pandas as pd
from googletrans import Translator
#%%
db = MongoClient('mongodb://akankshanb:HavanKarenge123@vpn.ssdorsey.com:27017/ml4p').ml4p

#%%
def modify_url(missing):
    '''
    :param missing: leftover urls not found
    '''
    modified = []
    for url in missing:
        url = url.replace('http://', '')
        url = url.replace('https://', '')
        url = url.replace('www.', '')
        url = url[:-1]
        modified.append(url)
    return modified

def get_data(modified, titles, source):
    '''
    :param source: source domain
    :param urls: urls to search
    :param titles: titles to search
    '''
    missing = []
    item = []
    for url in modified:
        data = db.articles.find_one(
            {
                'source_domain': source,
                'url' : {'$regex': url}
            }
        )
        if data==None:
            missing.append(url)
        else:
            item.append((data,url))
    return item, missing  
    
def get_data1(modified, source):
    '''
    :param modified: modified urls for search
    :param source: source domain
    '''
    item = []
    missing = []
    for url,title in modified:
        data = [i for i in db.articles.find_one(
            {
                'source_domain': source,
                'url' : {'$regex' : url}
            }
        )]
        if len(data)==0:
            missing.append((url,title))
        else:
            item.append(data)
    return item ,missing

def match_title(still_missing, source):
    '''
    :param still_missing: not found urls, if present
    :param source: source domain
    '''
    item = []
    missing = []
    for url,title in still_missing:
        data = [i for i in db.articles.find_one(
                {
                    'source_domain': source,
                    'title' : { '$regex': title}
                }
            )]
        if len(data)==0:
            missing.append((url,title))
        else:
            item.append(data)
    return item, missing

def get_description(i, translator):
    '''
    :param i: input data to be translated
    :param translator: object
    '''
    new_dict = {} 
    two_sentences = ".".join(i['description'].split("\n")[0:2])
    ttext = translator.translate(two_sentences).text
    ttitle = translator.translate(i['title']).text
    new_dict = i
    new_dict['translated_text'] = ttext
    new_dict['translated_title'] = ttitle
    return new_dict

def get_text(i, translator):
    '''
    :param i: input data to be translated
    :param translator: object
    '''
    new_dict = {}
    twoParas = ".".join(i['maintext'].split("\n")[0:2])
    two_sentences = ".".join(twoParas.split(".")[0:2])
    ttext = translator.translate(two_sentences).text
    ttitle = translator.translate(i['title']).text
    new_dict = i
    new_dict['translated_text'] = ttext
    new_dict['translated_title'] = ttitle
    return new_dict

# %%
df = pd.read_csv('/Users/akankshabhattacharyya/Documents/DukePeaceProject/CSV/danas_updated.csv')
df = df.dropna(subset=['URL'])
urls = df['URL']
titles = df['Title']
source = 'danas.rs'

modified = modify_url(urls)
#%%
item, missing = get_data(modified, titles, source)
# item1, missing1 = get_data1(modified, source)
# item2, missing2 = match_title(missing1, source)
# flatten = [i for sublist in hold for i in sublist]

#%%
not_translated = []
translated = []
for i in item:
    translator = Translator()
    if i[0]['maintext'] is None:
        if i[0]['description'] is None:
            not_translated.append(i)
        else:
            translated.append((get_description(i[0], translator), i[1]))
    else:
        translated.append((get_text(i[0], translator), i[1]))


# %%
import csv
path = '/Users/akankshabhattacharyya/Documents/DukePeaceProject/CSV/danas_updated_trans.csv'
df = pd.DataFrame(columns = ['date_publish', 'source_domain','URL','Title','translated_title','description','maintext','translated_text']) 
for i in translated:
    new_row = {'date_publish': i[0]['date_publish'], 'description': i[0]['description'], 'Title':i[0]['title'], 'source_domain': i[0]['source_domain'], 'maintext':i[0]['maintext'],'URL':i[1], 'translated_text':i[0]['translated_text'],'translated_title':i[0]['translated_title']}
    df = df.append(new_row, ignore_index=True)
df.to_csv(path, index=False)

    
# %%
orgPath = '/Users/akankshabhattacharyya/Documents/DukePeaceProject/CSV/danas_updated.csv'
path2Merge = '/Users/akankshabhattacharyya/Documents/DukePeaceProject/CSV/danas_updated_trans.csv'
df1 = pd.read_csv(orgPath)
df1 = df1.dropna(subset=['URL'])
df1['URL'] = modify_url(df1['URL'])
df2 = pd.read_csv(path2Merge)
df_inner = pd.merge(df1, df2, on='URL', how='left')

#%%
# reqdColumns = ['URL', 'source_domain', 'translated_title', 'maintext','description','translated_text','civic_event0','civic_event1','civic_event2','RAI_Event0','RAI_Event1','RAI_Event2','civic_code_in_db']
df_inner1 = df_inner[reqdColumns]
# %%
new_path = '/Users/akankshabhattacharyya/Documents/DukePeaceProject/CSV/danasTrans_updated.csv'
df_inner.to_csv(new_path, index=False)
# %%
len(item)
# %%
def modify(urls):
    for url in urls:
        url = url.replace('http://', '')
        url = url.replace('https://', '')
        url = url.replace('www.', '')
        url = url[:-1]
    return urls
# %%
