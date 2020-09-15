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
    for i in missing:
        url = i[0]
        title = i[1]
        url = url.replace('http://', '')
        url = url.replace('https://', '')
        url = url.replace('www.', '')
        url = url[:-1]
        modified += [(url,title.strip())]
    return modified

def get_data(urls, titles, source):
    '''
    :param source: source domain
    :param urls: urls to search
    :param titles: titles to search
    '''
    missing = []
    item = []
    for url,title in zip(urls, titles):
        data = [i for i in db.articles.find(
            {
                'source_domain': source,
                'url' : url
            }
        )]
        if len(data)==0:
            missing.append((url,title))
        else:
            item.append(data)
    return item, missing  
    
def get_data1(modified, source):
    '''
    :param modified: modified urls for search
    :param source: source domain
    '''
    item = []
    missing = []
    for url,title in modified:
        data = [i for i in db.articles.find(
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
        data = [i for i in db.articles.find(
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
df = pd.read_csv('/Users/akankshabhattacharyya/Documents/DukePeaceProject/CSV/insajder.csv')
df = df.dropna(subset=['URL'])
urls = df['URL']
titles = df['Title']
source = 'insajder.net'

item, missing = get_data(urls, titles, source)
modified = modify_url(missing)
item1, missing1 = get_data1(modified, source)
item2, missing2 = match_title(missing1, source)

hold = []
hold = item + item1 + item2
flatten = [i for sublist in hold for i in sublist]

not_translated = []
translated = []
for i in flatten:
    translator = Translator()
    if i['maintext'] is None:
        if i['description'] is None:
            not_translated.append(i)
        else:
            translated.append(get_description(i, translator))
    else:
        translated.append(get_text(i, translator))


# %%
import csv
path = '/Users/akankshabhattacharyya/Documents/DukePeaceProject/CSV/insajder_trans.csv'
df = pd.DataFrame(columns = ['date_publish', 'description','title','source_domain','maintext','url','translated_text','translated_title']) 
for i in translated:
    new_row = {'date_publish': i['date_publish'], 'description': i['description'], 'title':i['title'], 'source_domain': i['source_domain'], 'maintext':i['maintext'],'url':i['url'], 'translated_text':i['translated_text'],'translated_title':i['translated_title']}
    df = df.append(new_row, ignore_index=True)
df.to_csv(path, index=False)

# %%
x = [h['translated_text'] for h in translated]
#%%
import json
with open('/Users/akankshabhattacharyya/Documents/DukePeaceProject/translated3.txt','w') as f:
    for i in x:
        f.write("%s\n" % i)