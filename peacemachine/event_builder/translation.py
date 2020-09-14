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

def get_description(not_translated):
    '''
    :param not_translated: getting info from description tag
    :param translator: google translator object
    '''
    translator = Translator()
    translated = []
    still_not_translated = []
    new_dict = {}
    for i in not_translated:
        if i['description'] is None:
            still_not_translated.append(i)
        else:
            two_sentences = ".".join(i['description'].split("\n")[0:2])
            ttext = translator.translate(two_sentences).text
            ttitle = translator.translate(i['title']).text
            new_dict = i
            new_dict['translated_text'] = ttext
            new_dict['translated_title'] = ttitle
            translated.append(new_dict)
    return translated,still_not_translated

def translate_data(inp):
    '''
    :param inp: input data to be translated
    '''
    translator = Translator()
    not_translated = []
    translated = []
    new_dict = {}
    for i in flatten:
        if i['maintext'] is None:
            not_translated.append(i)
        else:
            twoParas = ".".join(i['maintext'].split("\n")[0:2])
            two_sentences = ".".join(twoParas.split(".")[0:2])
            ttext = translator.translate(two_sentences).text
            ttitle = translator.translate(i['title']).text
            new_dict = i
            new_dict['translated_text'] = ttext
            new_dict['translated_title'] = ttitle
            translated.append(new_dict)
    trans, nottrans = get_description(not_translated)
    res = trans + translated
    return res,nottrans

# %%
df = pd.read_csv('/Users/akankshabhattacharyya/Documents/DukePeaceProject/CSV/rsn1info.csv')
df = df.dropna(subset=['URL'])
urls = df['URL']
titles = df['Title']
source = 'rs.n1info.com'

item, missing = get_data(urls, titles, source)
modified = modify_url(missing)
item1, missing1 = get_data1(modified, source)
item2, missing2 = match_title(missing1, source)

hold = []
hold = item + item1 + item2
flatten = [i for sublist in hold for i in sublist]

#%%
result,nottrans = translate_data(flatten)

# %%
x = [h for h in hold if len(h)>1]
# %%
translator = Translator()

twoParas = ".".join(result[7]['description'].split("\n")[0:2])
two_sentences = ".".join(twoParas.split(".")[0:2])
ttext = translator.translate(two_sentences).text
ttext
# %%
