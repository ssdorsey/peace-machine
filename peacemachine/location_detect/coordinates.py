#%%
from pymongo import MongoClient
import sys
import pandas as pd
from itertools import groupby
from datetime import datetime,timedelta
# sys.path.append('../../mordecai-env/lib/python3.7/site-packages')
from mordecai import Geoparser
import spacy  
import json  
import wptools                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      

class Location():
    def __init__(self, *args):
        self.geo = Geoparser()
        self.demonymMapping = self.initialize_mapping()
        self.nlp = spacy.load("en_core_web_sm")
        self.wikimodel = spacy.load("xx_ent_wiki_sm")
    
    def initialize_mapping(self):
        '''
        setup a hashmap of nationality - country
        '''
        mapping = {}
        with open('countries.json') as f:
            data = json.loads(f.read())
        for d in data:
            nationality = d['demonyms']['eng']['m']
            country = d['cca3']
            if nationality not in mapping:
                mapping[nationality] = country
        return mapping
    
    def get_demonym(self,text):
        '''
        get country from nationality
        :param text: String nationality
        '''
        if text in self.demonymMapping:
            return self.demonymMapping[text]

    def get_locs(self,location, key):
        '''
        returns dict of location
        :param location: geoparser output
        :param key: location grabbed from text
        '''
        hold_loc_dic = dict()
        if 'country_predicted' in location.keys():
            country = location['country_predicted']
            hold_loc_dic[country] = []
            if 'geo' in location.keys():
                geodict = location['geo']
                # if 'admin1' in geodict.keys() and geodict['admin1']!='NA':
                #     geoVal = geodict['admin1']
                #     hold_loc_dic[country].append(geoVal)
                if 'place_name' in geodict.keys():
                    geoPla = geodict['place_name']
                    hold_loc_dic[country].append(geoPla)
        else:
            if 'geo' in location.keys():
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

    def get_max_occ(self,grouped):
        '''
        returns max occurence of location word in text
        :param grouped: grouped data
        '''
        maximum = -1
        for key,group in grouped:
            maximum = max(maximum, len(list(group))) 
        return maximum
    
    def get_all_locations(self,grouped, max_occ):
        '''
        returns dict of final locations
        :param grouped: grouped data
        :param max_occ: freq of each word
        '''
        locations = dict()
        for key,group in grouped:
            location_list = list(group)
            if len(location_list)== max_occ:
                top_loc = location_list
                if len(top_loc) > 0:
                    locations.update(self.get_locs(top_loc[0], key))
        return locations
    
    def parse_location(self,text):
        '''
        returns final locations from text
        :param text: string
        '''
        locations = {}
        try:
            loc = self.geo.geoparse(text)
            for l in loc:
                l['word'] = l['word'].lower()
            loc = sorted(loc, key = lambda x: x['word'])
            grouped = groupby(loc, key=lambda x:x['word'])
            max_occ = self.get_max_occ(grouped)
            grouped = groupby(loc, key=lambda x:x['word'])
            locations = self.get_all_locations(grouped, max_occ)
            return locations
        except ValueError:
            loc = None

    def split_and_get_loc(self,text):
        names = text.split(" ")
        loc_entities = dict()
        for name in names:
            doc = self.nlp(name)
            for X in doc.ents:
                # print(X.label_, X.text)
                if X.label_=="GPE":
                    loc_entities[X.text] = []
        return loc_entities
    
    def wiki_search(self, text):
        '''
        search for names on wiki
        :param text: String containing name
        '''
        try:
            info = wptools.page(text).get_parse()
            place = info.data['infobox']['birth_place']
            return self.split_and_get_loc(place)
        except:
            return {}
        
        
    
    def get_entity(self,text):
        '''
        return dict of location entities
        :param text: string containing news title
        '''
        doc = self.nlp(text)
        loc_entities = dict()
        for X in doc.ents:
            if X.label_=="GPE":
                loc_entities[X.text] = []
            elif X.label_=="PERSON":
                loc_entities.update(self.wiki_search(X.text))
            elif X.label_=="ORG":
                loc_entities.update(self.split_and_get_loc(X.text))
                pass
            elif X.label_=="NORP":
                loc_entities[self.get_demonym(X.text)] = []
        return loc_entities      
    

def get_event_data(dt, source,db):
    '''
    :param dt - datetime
    :param source - source name
    '''
    col_name = f'{dt.year}-{dt.month}-events'
    d = [i for i in db[col_name].find(
        {
            'source_domain': source
            
        }
    )]
    return d  

    
def main():
    db = MongoClient('mongodb://akankshanb:HavanKarenge123@vpn.ssdorsey.com:27017/ml4p').ml4p
    dt = datetime(2019,1,1)
    source = 'bbc.com'
    dd = get_event_data(dt, source,db)
    df = pd.DataFrame([i for i in dd])
    df.dropna(subset=['title'])
    print("------data collected-----")
    # df1 = df[0:50]       
    text = df1['title']
    hold_loc = []
    location = Location()
    # print(location.wiki_search('1919: The Year of the Crack-Up'))
    hold_loc = []
    print("-------extracting locations------")
    for t in text:
        if location.parse_location(t):
            hold_loc+= [location.parse_location(t)]
        elif location.get_entity(t):
            hold_loc+= [location.get_entity(t)]
        else:
            hold_loc += [{}]
        # print(t, "location dict", hold_loc[-1])
    # print(len(hold_loc), df1.shape)
    df1['location'] = hold_loc
    
if __name__ == '__main__':
    main()