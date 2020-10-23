#%%
from pymongo import MongoClient
import sys
import pandas as pd
from itertools import groupby
from datetime import datetime
# sys.path.append('../../mordecai-env/lib/python3.7/site-packages')
from mordecai import Geoparser
import spacy                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
nlp = spacy.load("en_core_web_sm")

db = MongoClient('mongodb://akankshanb:HavanKarenge123@vpn.ssdorsey.com:27017/ml4p').ml4p

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

def get_locs(location, key):
    '''
    :param location: geo dict from geoparser
    :param key: location name from text
    '''
    hold_loc_dic = dict()
    # print(location)
    if 'country_predicted' in location.keys():
        country = location['country_predicted']
        hold_loc_dic[country] = []
        if 'geo' in location.keys():
            geodict = location['geo']
            if 'admin1' in geodict.keys() and geodict['admin1']!='NA':
                geoVal = geodict['admin1']
                hold_loc_dic[country].append(geoVal)
            if 'place_name' in geodict.keys():
                geoPla = geodict['place_name']
                hold_loc_dic[country].append(geoPla)
    else:
        if 'geo' in location.keys():
            print("country not found")
            geodict = location['geo']
            if 'admin1' in geodict.keys() and geodict['admin1']!='NA':
                geoVal = geodict['admin1']
                hold_loc_dic[geoVal] = []
                if 'place_name' in geodict.keys():
                    geoPla = geodict['place_name']
                    hold_loc_dic[geoVal].append(geoPla)
                else:
                    hold_loc_dic[geoVal].append(key)
    return hold_loc_dic

def get_max_occ(grouped):
    '''
    find max occurence of word
    :param grouped: grouped data
    '''
    maximum = -1
    for key,group in grouped:
        maximum = max(maximum, len(list(group))) 
    return maximum

def get_locations(grouped, max_occ):
    '''
    get all locations possible
    :param grouped: grouped data
    '''
    locations = dict()
    for key,group in grouped:
        location_list = list(group)
        if len(location_list)== max_occ:
            top_loc = location_list
            if len(top_loc) > 0:
                locations.update(get_locs(top_loc[0], key))
    return locations

def parse_location(text):
    '''
    :param text: string containing news title
    '''
    locations = {}
    try:
        loc = geo.geoparse(t)
        for l in loc:
            l['word'] = l['word'].lower()
        loc = sorted(loc, key = lambda x: x['word'])
        grouped = groupby(loc, key=lambda x:x['word'])
        max_occ = get_max_occ(grouped)
        grouped = groupby(loc, key=lambda x:x['word'])
        locations = get_locations(grouped, max_occ)
        return locations
    except ValueError:
        loc = None

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
    
dt = datetime(2019,1,1)
source = 'nytimes.com'
dd = get_event_data(dt, source)
df = pd.DataFrame([i for i in dd])
df1 = df.dropna(subset=['title'])
df1 = df1[50:100]
text = df1['title']
hold_loc = []
for t in text:
    hold_loc+= [parse_location(t)]
df1['location'] = hold_loc

##leftover whatever could not be found by mordecai, using NER Spacy
df_left = df1[['title','location']][df1['location']=={}] 
hold_loc = []
for rowIndex in df_left.index:
    hold_loc_dict = {}
    rowIndex = int(rowIndex)
    text = df_left.loc[rowIndex, 'title']
    loc_entities = get_entity(text)
    for l in loc_entities:
        hold_loc_dict[l] = []
    df1.at[rowIndex, "location"] = hold_loc_dict
# %%

get_entity('Macron Vows Order ‘Without Compromise’ in Rebuke to Yellow Vest Protests')

# %%
