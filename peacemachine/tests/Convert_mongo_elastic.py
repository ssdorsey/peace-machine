import os
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from tqdm import tqdm
import pandas as pd
import numpy as np
from urllib.parse import urlparse
from datetime import datetime
from dateutil.parser import parse
from dateutil.parser import ParserError
import geocoder

if os.getlogin() != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
    es =  Elasticsearch(['http://192.168.176.240:9200'])
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p
    es =  Elasticsearch(['http://localhost:9200'])#,  ca_certs=False, verify_certs=False)



# articles = db['articles']
# events = db['events']
# # lac = db['lac']


def is_duplicate(_key, _value, index):
    """
    checks for a duplicate document on a single key/field in the named index
    """
    res = es.search(
        index=index,
        body={
            "query": {
                "term": {
                    _key: {
                        "value": _value,
                        "boost": 1.0
                    }
                }
            }
        }
    )
    if res['hits']['total']['value'] == 0:
        return False
    else:
        return True

def strip_url(url):
    """
    strips a url of all the fluff
    """
    parsed = urlparse(url)
    sturl = parsed.netloc + parsed.path
    # strip www.
    sturl = sturl.replace('www.', '')
    return sturl


def create_id(doc):
    """
    creates an id from a doc
    """
    return(str(int(_doc['date_publish'].timestamp())) + strip_url(_doc['url'])[:300])

# # create the index
# if 'articles' not in  es.indices.get_alias("*"):
#     request_body = {
#         "settings" : {
#             "number_of_shards": 10,
#             "number_of_replicas": 0
#         }, 
#         "mappings": {
#             "properties": {
#                 "url": {
#                     "type": "keyword"
#                 }, 
#                 "source_domain": {
#                     "type": "keyword"
#                 }, 
#                 "date_publish": {
#                     "type": "date"
#                 }
#             }
#         }
#     }

#     es.indices.create(index='articles', body = request_body, ignore=400)

keep_keys = {
    'authors',
    'date_download', 
    'date_modify', 
    'date_publish', 
    'description', 
    'image_url', 
    'language', 
    'title',
    'title_page', 
    'source_domain', 
    'maintext', 
    'url'
}

# # Pull from mongo and dump into ES using bulk API
# actions = []
# for _doc in tqdm(articles.find(), total=articles.estimated_document_count()):
#     # remove the fields I don't want
#     _doc = {k:v for k,v in _doc.items() if k in keep_keys}
#     # must have date_publish in proper format
#     if 'date_publish' not in _doc:
#         continue
#     if not _doc['date_publish']:
#         continue
#     # must convert to datetime
#     if not isinstance(_doc['date_publish'], datetime):
#         try:
#             _doc['date_publish'] = parse(_doc['date_publish'])
#         except ParserError:
#             continue
#     if _doc['date_publish'].year <= 1970:
#         continue
#     # replace NaN w/ None
#     for k,v in _doc.items():
#         if isinstance(v, list):
#             continue
#         if pd.isnull(v):
#             _doc[k] = None
#     # insert 
#     # es.index(index='articles', id=create_id(_doc), body=_doc)
#     # build up the inserts
#     action = {
#             "index": {
#                     "_index": 'articles',
#                     "_id": create_id(_doc)
#                     }
#     }
#     actions.append(action)
#     actions.append(_doc)
#     if len(actions) > 100:
#         res = es.bulk(index = 'articles', body = actions)
#         actions = []
#         es.indices.clear_cache(index='articles')

# # get the left-overs
# if len(actions) > 0:
#     res = es.bulk(index = 'articles', body = actions)
#     es.indices.clear_cache(index='articles')

# # ---------------------------------------------------------------------------
# # events
# # ---------------------------------------------------------------------------
if 'events' not in  es.indices.get_alias("*"):
    request_body = {
        "settings" : {
            "number_of_shards": 5,
            "number_of_replicas": 0
        }, 
        "mappings": {
            "properties": {
                "url": {
                    "type": "keyword"
                }, 
                "source_domain": {
                    "type": "keyword"
                }, 
                "event_type": {
                    "type": "keyword"
                }, 
                "bad_location": {
                    "type": "keyword"
                }, 
                "date_publish": {
                    "type": "date"
                }, 
                "location": {
                    "type": "geo_point"
                }
            }
        }
    }
    es.indices.create(index='events', body = request_body, ignore=400)

keep_keys = {
    'authors',
    'date_publish', 
    'bad_location',
    'title',
    'source_domain', 
    'url', 
    'event_type', 
    'model_outputs', 
    'model_max', 
    'geocoder'
}

# Pull from mongo and dump into ES using bulk API
actions = []
for _doc in tqdm(db['2020-6-events'].find(), 
                total=db['2020-6-events'].estimated_document_count()):
    # remove the fields I don't want
    _doc = {k:v for k,v in _doc.items() if k in keep_keys}
    # geocode for mapping
    if 'bad_location' not in _doc or not _doc['bad_location']:
        continue
    g = geocoder.arcgis(_doc['bad_location']).json
    _doc['location'] = {
        'lat': g['lat']+np.random.randn(),
        'lon': g['lng']+np.random.randn()
    }
    # replace NaN w/ None
    for k,v in _doc.items():
        if isinstance(v, list):
            continue
        if pd.isnull(v):
            _doc[k] = None
    # insert 
    # es.index(index='events', id=create_id(_doc), body=_doc)            
    # build up the inserts
    action = {
            "index": {
                    "_index": 'events',
                    "_id": create_id(_doc)
                    }
    }
    actions.append(action)
    actions.append(_doc)
    if len(actions) > 200:
        res = es.bulk(index = 'events', body = actions)
        actions = []
        # es.indices.clear_cache(index='events')


# # # get the leftovers 
# # if len(actions) > 0:
# #     res = es.bulk(index = 'events', body = actions)
