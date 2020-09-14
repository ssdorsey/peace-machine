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

#%%
translator = Translator()
not_translated = []
translated = []
for i in flatten:
    if i['maintext'] is None:
        not_translated.append(i)
    else:
        twoParas = ".".join(i['maintext'].split("\n")[0:2])
        two_sentences = ".".join(twoParas.split(".")[0:2])
        s = translator.translate(two_sentences).text
        new_dict = i
        new_dict['translated'] = s
        translated.append(new_dict)
#%%
trans, nottrans = get_description(not_translated)
res = trans + translated

#%%
def get_description(not_translated):
    '''
    :param not_translated: getting info from description tag
    :param translated: already translated list
    '''
    translated = []
    still_not_translated = []
    for i in not_translated:
        if i['description'] is None:
            still_not_translated.append(i)
        else:
            two_sentences = ".".join(i['description'].split("\n")[0:2])
            s = translator.translate(two_sentences).text
            new_dict = i
            new_dict['translated'] = s
            translated.append(new_dict)
    return translated,still_not_translated

#%%
translator.translate(two_sentences).text
   

# translator.translate(hold[0]['maintext'][])
# %%
missing_maintext = [i for i in db.articles.find(
        {
            'source_domain': 'insajder.net',
            'title' : { '$regex': 'Protest ispred Skupštine: Povod obraćanje predsednika, uzroci različiti, organizatori nepoznati'}
            
        }
    )]
missing_maintext
# %%
