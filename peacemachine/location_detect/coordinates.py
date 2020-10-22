#%%
from pymongo import MongoClient
import sys
import pandas as pd
from itertools import groupby
from datetime import datetime
from mordecai import Geoparser
import spacy
nlp = spacy.load("en_core_web_sm")

db = MongoClient('mongodb://akankshanb:HavanKarenge123@vpn.ssdorsey.com:27017/ml4p').ml4p
#%%
geo = Geoparser()
#%%
def get_event_data(dt, source):
    '''
    :param dt - datetime
    '''
    col_name = f'{dt.year}-{dt.month}-events'
    d = [i for i in db[col_name].find(
        {
            'source_domain': source
            
        }
    )]
    return d
#%%
def get_locs(location, key):
    '''
    :param location: geo dict from geoparser
    :param key: location name from text
    '''
    hold_loc_dic = dict()
    if 'country_predicted' in location.keys():
        country = location['country_predicted']
        hold_loc_dic[country] = []
        hold_loc_dic[country].append(key)
        if 'geo' in location.keys():
            geodict = location['geo']
            if 'admin1' in geodict.keys():
                geoVal = geodict['admin1']
                hold_loc_dic[country].append(geoVal)
    else:
        if 'geo' in location.keys():
            geodict = location['geo']
            if 'admin1' in geodict.keys():
                geoVal = geodict['admin1']
                hold_loc_dic[geoVal] = []
                hold_loc_dic[geoVal].append(key)
    return hold_loc_dic
#%%
def parse_location(text):
    '''
    :param text: string containing news title
    '''
    max_occ = -1
    locations = {}
    top_loc = []
    try:
        loc = geo.geoparse(t)
        for l in loc:
            l['word'] = l['word'].lower()
        loc = sorted(loc, key = lambda x: x['word'])
        grouped = groupby(loc, key=lambda x:x['word'])
        for key,group in grouped:
            location_list = list(group)
            if len(location_list)>0 and len(location_list) >= max_occ:
                max_occ = len(location_list)
                top_loc = location_list
        if len(top_loc) > 0:
            locations = get_locs(top_loc[0], key)
        return locations
    except ValueError:
        loc = None
#%%     
def get_entity(text):
    '''
    :param text: string containing news title
    '''
    doc = nlp(text)
    loc_entities = []
    for X in doc.ents:
        if X.label_=="GPE":
            loc_entities += [X.text]
    return loc_entities
    
#%%
dt = datetime(2019,1,1)
source = 'reuters.com'
dd = get_event_data(dt, source)
df = pd.DataFrame([i for i in dd])
df1 = df.dropna(subset=['title'])
df1 = df1[0:40]
text = df1['title']
hold_loc = []
for t in text:
    hold_loc+= [parse_location(t)]
df1['location'] = hold_loc

#%%
df_left = df1[['title','location']][df1['location']=={}]
# %%
hold_loc = []
for rowIndex in df_left.index:
    hold_loc_dict = {}
    rowIndex = int(rowIndex)
    text = df_left.loc[rowIndex, 'title']
    loc_entities = get_entity(text)
    for l in loc_entities:
        hold_loc_dict[l] = []
    df1.at[rowIndex, "location"] = hold_loc_dict