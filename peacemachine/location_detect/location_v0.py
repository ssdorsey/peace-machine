from pymongo import MongoClient
import sys
import re
import time
import pandas as pd
from itertools import groupby
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from mordecai import Geoparser
import spacy  
import json  
import wptools
import concurrent.futures


def calculate_time(func): 
      
    # added arguments inside the inner1, 
    # if function takes any arguments, 
    # can be added like this. 
    def inner1(*args, **kwargs): 
  
        # storing time before function execution 
        begin = time.time() 
          
        func(*args, **kwargs) 
  
        # storing time after function execution 
        end = time.time() 
        print("Total time taken in : ", func.__name__, end - begin) 
    return inner1


def location_pipe(uri, batch_size):
    """
    :param uri: The MongoDB uri for connecting to the main DB
    :param batch_size: The default batch size for the selected operation
    """
    db = MongoClient(uri).ml4p
    locs = Location(uri, batch_size)
    locs.run()

class Location():
    
    def __init__(self, mongo_uri, batch_size):
        self.mongo_uri = mongo_uri
        self.batch_size = batch_size
        self.db = MongoClient(mongo_uri).ml4p

        self.geo = Geoparser(lru_cache = 1000)
        self.demonymMapping = self.initialize_mapping()
        self.nlp = spacy.load("en_core_web_lg")
        self.wikimodel = spacy.load("xx_ent_wiki_sm")
        
    def initialize_mapping(self):
        '''
        setup a hashmap of nationality - country
        '''
        mapping = {}
        with open('data/countries.json') as f:
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
            # print("GEOPARSED LOCATION", locations)
            return locations
        except ValueError:
            # print("NOT GEOPARSED")
            loc = None


    def split_and_get_loc(self,text):
        names = text.split(",")
        loc_entities = dict()
        for name in names:
            name = name.strip()
            doc = self.nlp(name)
            for X in doc.ents:
                if X.label_=="GPE":
                    return X.text
        return None
    

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
            return None
        
   
    def get_entity(self,text):
        '''
        return dict of location entities
        :param text: string containing news title
        '''
        doc = self.nlp(text)
        loc_entities = dict()
        entity_set = set()
        for X in doc.ents:
            if X.text in entity_set:
                continue
            if X.label_=="GPE":
                loc_entities[X.text] = []
            elif X.label_=="PERSON":
                wiki_l = self.wiki_search(X.text)
                loc_entities[wiki_l] = []
            elif X.label_=="ORG":
                org_l = self.split_and_get_loc(X.text)
                loc_entities[org_l] = []
            elif X.label_=="NORP":
                demo_l = self.get_demonym(X.text)
                loc_entities[demo_l] = []
            entity_set.add(X.text)
        return loc_entities  


    def fix_maintext(self, mt):
        try:
            mt = re.sub(r'(\n)', '. ', mt)
            mt = re.sub(r'(-{3,})', ' ', mt)
            mt = mt[0:300]
        except AttributeError:
            return None
        except TypeError:
            return None
        return mt


    def batch_locate(self, titles):
        '''
        :param titles: tuple of ids,titles
        :return: list of location keys
        '''
        res = []
        for _id,t in titles:
            from_mordecai = self.parse_location(t)
            from_spacy = None
            if not from_mordecai:
                from_spacy = self.get_entity(t)
            if from_mordecai:
                res+= [(_id, from_mordecai)]
            elif from_spacy:
                res+= [(_id, from_spacy)]
            else:
                res += [(_id, {})]
            # print("RESULTS:", res)
        return res

    @calculate_time
    def location_start(self):
        '''
            pull data from db
        '''
        _ids = [_doc['_id'] for _doc in self.list_docs]

        titles = [(_doc['_id'], _doc['title']) for _doc in self.list_docs]

        maintext = [(_doc['_id'], self.fix_maintext(_doc['maintext'])) for _doc in self.list_docs]

        start = time.time()
        # located_titles = self.batch_locate(titles)
        located_maintext = self.batch_locate(maintext)
        end = time.time()
        print('Articles located with time:', end-start)

        # print("BATCH OF LOCATED STORIES", located_titles)

        # insert into DB
        print("Article_collection:", self.colname)

        # for iter1,iter2 in zip(located_titles, located_maintext):
        for _id,loc in located_maintext:
            # iter1[1].update(iter2[1])
            # if None in iter1[1]:
            if None in loc:
                # del iter1[1][None]
                del loc[None]
        #     # insert into article-yyy-mm
            # print(iter1[1])
            print(loc)
            try:
                self.db[self.colname].update_one(
                    {'_id': _id} , #iter1[0] 
                    {'$set': {
                        'mordecai_locations': loc #iter1[1]
                    }}
                )
            except:
                print('ERROR INSERTING')

        print("INSERTED")

    def run_thread(self,dt):

        self.colname = f'articles-{dt.year}-{dt.month}'

        cursor = self.db[self.colname].find(
            {
                # 'source_domain': source,
                'source_domain' : {'$in' : ['reuters.com','bbc.com','nytimes.com','washingtonpost.com','aljazeera.com','theguardian.com','france24.com','wsj.com','csmonitor.com','themoscowtimes.com','xinhuanet.com','scmp.com']},
                'language' : 'en',
                'include': True,
                # 'title':{'$ne': ''},
                # 'title':{'$not': {'$type': 'null'}},
                'maintext':{'$ne': ''},
                'maintext':{'$not': {'$type': 'null'}},
                'mordecai_locations' : {'$exists': False}
            }
        ).batch_size(self.batch_size)

        self.list_docs = []

        for _doc in tqdm(cursor):
            self.list_docs.append(_doc)
            if len(self.list_docs) >= self.batch_size:
                print('Detecting Location')
                try:
                    self.location_start()
                except ValueError:
                    print('ValueError')
                except AttributeError:
                    print('AttributeError')
                self.list_docs = []

        # handle whatever is left over
        self.location_start()
        self.list_docs = []


    def run(self):
        '''
            main function to run the location
        '''
        # dates = pd.date_range('2020-1-1','2021-1-31', freq='M')
        
        # with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        #     for dt in dates:
        #         print("THREADS:", dt)
        #         executor.submit(self.run_thread, dt)
        dt  = pd.to_datetime('2020-8-1')
        self.run_thread(dt)


def main():
    uri = 'mongodb://akankshanb:HavanKarenge123@152.3.22.155/ml4p'
    location_pipe(uri,64)
    
if __name__ == '__main__':
    main()
