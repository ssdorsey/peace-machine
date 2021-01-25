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

        self.geo = Geoparser()
        self.demonymMapping = self.initialize_mapping()
        self.nlp = spacy.load("en_core_web_lg")
        self.wikimodel = spacy.load("xx_ent_wiki_sm")
        self.dist_threshold = 0.059
        
    def initialize_mapping(self):
        '''
        setup a hashmap of nationality - country
        '''
        mapping = {}
        with open('peacemachine/location_detect/countries.json') as f:
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

    def get_loc(self, loc, all_locations):
        '''
        returns dict of location
        :param location: geoparser output
        :param key: location grabbed from text
        '''
        if 'country_predicted' in loc.keys():
            country = loc['country_predicted']
            if country not in all_locations:
                all_locations[country] = []
            if 'geo' in loc.keys():
                geodict = loc['geo']
                if 'place_name' in geodict.keys():
                    geoPla = geodict['place_name']
                    if geoPla not in all_locations[country]:
                        all_locations[country].append(geoPla)

    def parse_location(self,text, all_locations):
        '''
        returns final locations from text
        :param text: string
        '''
        try:
            loc = self.geo.geoparse(text)
            loc = sorted(loc, key = lambda x: x['country_conf'], reverse=True)
            try:
                max_conf = loc[0]['country_conf']
            except IndexError:
                pass
            for l in loc:
                if max_conf - l['country_conf'] <= self.dist_threshold:
                #Then we can use this location detected
                        self.get_loc(l, all_locations)
        except ValueError:
            loc = None
        except TypeError:
            text = None

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
            return place
        except:
            return None
        
    def get_entity(self,text, all_locations):
        '''
        return dict of location entities
        :param text: string containing news title
        '''
        doc = self.nlp(text)
        loc_entities = dict()
        entity_set = set()
        for X in doc.ents:
            if X.text in entity_set or X.text in all_locations:
                continue
            if X.label_=="GPE":
                self.parse_location(X.text, all_locations)
                # loc_entities[X.text] = []
            elif X.label_=="PERSON":
                wiki_l = self.wiki_search(X.text)
                if wiki_l:
                    self.parse_location(wiki_l, all_locations)
                # loc_entities[wiki_l] = []
            elif X.label_=="ORG":
                # org_l = self.split_and_get_loc(X.text)
                pass
                # loc_entities[org_l] = []
            elif X.label_=="NORP":
                demo_l = self.get_demonym(X.text)
                if demo_l not in all_locations.keys():
                    all_locations[demo_l] = []
            entity_set.add(X.text)  

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
            all_locations = {}
            self.parse_location(t, all_locations)
            from_spacy = None
            if not all_locations:
                self.get_entity(t, all_locations)
            res+= [(_id, all_locations)]
            # if all_locations:
            #     res+= [(_id, all_locations)]
            # elif from_spacy:
            #     res+= [(_id, all_locations)]
            # else:
            #     res += [(_id, {})]
        return res

    @calculate_time
    def location_start(self):
        '''
            pull data from db
        '''
        _ids = [_doc['_id'] for _doc in self.list_docs]

        titles = [(_doc['_id'], _doc['title']) for _doc in self.list_docs]

        maintext = [(_doc['_id'], self.fix_maintext(_doc['maintext'])) for _doc in self.list_docs]

        # located_titles = self.batch_locate(titles)
        located_maintext = self.batch_locate(maintext)

        # print("BATCH OF LOCATED STORIES", located_titles)

        # insert into DB
        # print("Article_collection:", self.colname)

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
                # 'civic1': {'$exists': True},
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
        # dates = pd.date_range('2012-1-1','2012-12-1', freq='M')
        
        # with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        #     for dt in dates:
        #         print("THREADS:", dt)
        #         executor.submit(self.run_thread, dt)
        dt  = pd.to_datetime('2019-11-1')
        # self.location_start()
        self.run_thread(dt)

        # for dt in dates:
        #     self.run_thread(dt)


def main():
    uri = 'mongodb://akankshanb:HavanKarenge123@152.3.22.155/ml4p'
    location_pipe(uri,64)
    
if __name__ == '__main__':
    main()
