"""
This script runs the eventclassifier but pulls in reverse
and inserts into the non-local server
"""
import os
import sys
from tqdm import tqdm
from joblib import Parallel, delayed
from simpletransformers.classification import ClassificationModel
import numpy as np
import traceback
from datetime import datetime
from dateutil.parser import ParserError
from dateutil.parser import parse

# from elasticsearch import Elasticsearch


from peacemachine.event_builder import helpers
# import helpers

from pymongo import MongoClient
if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p

# es =  Elasticsearch(['http://192.168.176.240:9200'])

model = ClassificationModel('roberta'
                            , 'peacemachine/data/finetuned-transformers/ModelOutput'
                            , num_labels=18
                            , args={
                                'n_gpu':1
                                , 'eval_batch_size':768})

label_dict = {
    0: 'violencelethal'
    , 1: 'arrest'
    , 2: 'protest'
    , 3: 'censor'
    , 4: 'disaster'
    , 5: 'legalchange'
    , 6: 'changeelection'
    , 7: 'purge'
    , 8: 'martiallaw'
    , 9: 'mobilizesecurity'
    , 10: 'coup'
    , 11: 'defamationcase'
    , 12: 'violencenonlethal'
    , 13: 'praise'
    , 14: 'threaten'
    , 15: 'cooperate'
    , 16: 'raid'
    , 17: 'changepower'
}

keep_keys = {
    '_id',
    'authors',
    'date_publish', 
    'title',
    'source_domain', 
    'url', 
    'event_type', 
    'model_outputs', 
    'model_max'
}

error_urls = []

def create_id(doc):
    """
    creates an id from a doc
    """
    return(str(int(_doc['date_publish'].timestamp())) + helpers.strip_url(_doc['url'])[:300])


def process_docs(list_docs, language='en'):
    """
    processes list of docs and returns extracted events
    """
    inserted_count = 0
    list_docs = Parallel(n_jobs=-2)(delayed(helpers.build_combined)(doc) for doc in list_docs)
    # list_docs = [helpers.build_combined(ld) for ld in list_docs]

    list_docs = [dd for dd in list_docs if 'combined' in dd and dd['combined']]

    list_docs = [dd for dd in list_docs if isinstance(dd['combined'], str)]
    # get the domain
    for doc in list_docs:
        doc['domain'] = helpers.pull_domain(doc['url'])

    ### get the location
    if language == 'en':
        bad_locations = Parallel(n_jobs=-2)(delayed(helpers.pull_country)(doc['combined']) for doc in list_docs)
        # bad_locations = [helpers.pull_country(ld['combined']) for ld in list_docs]
        for nn, doc in enumerate(list_docs):
            doc['bad_location'] = bad_locations[nn]
            if not doc['bad_location'] and doc['domain'] in helpers.domain_locs:
                doc['bad_location'] = helpers.domain_locs[doc['domain']]

    if language != 'en':
        for doc in list_docs:
            if doc['domain'] in helpers.domain_locs:
                doc['bad_location'] = helpers.domain_locs[doc['domain']]

    for doc in list_docs:
        if 'bad_location' not in doc:
            doc['bad_location'] = ''

    ### do the predictions
    text = [doc['combined'] for doc in list_docs if len(doc['combined']) > 0]
    if len(text) == 0:
        return
    preds, model_outputs = model.predict(text)
    # modify outputs
    model_max = [float(max(mo)) for mo in model_outputs]
    event_types = [label_dict[ii] for ii in preds]

    for ii in range(len(model_max)):
        if model_max[ii] < 7:
            event_types[ii] = '-999'

    for nn, ld in enumerate(list_docs):
        ld['event_type'] = event_types[nn]
        ld['model_outputs'] = [float(mo) for mo in model_outputs[nn]]
        ld['model_max'] = model_max[nn]

    # for doc in list_docs:
    #     if 'eventExtracted' in doc:
    #         doc['eventExtracted'] += 1
    #     else: 
    #         doc['eventExtracted'] = 1
    # db.events.insert_many(list_docs)
    
    ### return to database
    list_docs = [ld for ld in list_docs if ld['date_publish']]
    for doc in list_docs:
        # only keep the keys I want
        doc = {k:v for k,v in _doc.items() if k in keep_keys}
        
        # first try mongo
        try:
            col_name = f"{doc['date_publish'].year}-{doc['date_publish'].month}-events"
            db[col_name].insert_one(doc)
            inserted_count += 1
        except:
            error_urls.append(doc['url'])

        # then elasticsearch
        # doc.pop('_id', None)
        # res = es.index(index="events", id=create_id(doc), body=doc)

    print(f'inserted_count: {inserted_count}')
    print(f'error count: {len(error_urls)}')

# --------------------------------------------------------
# ENGLISH
# --------------------------------------------------------
print('STARTING ENGLISH')

cursor = db['articles'].find(
    {'language':'en'}
).sort([('_id', -1)])

missing_date = []
hold_ee = []
count = 0
for _doc in tqdm(cursor):

    # deal with language
    if 'language' in _doc:
        if _doc['language'] != 'en':
            continue

    # deal with missing dates
    if 'date_publish' not in _doc:
        missing_date.append(_doc['url'])
        continue

    if not _doc['date_publish']:
        missing_date.append(_doc['url'])
        continue

    if not isinstance(_doc['date_publish'], datetime):
        try:
            _doc['date_publish'] = parse(_doc['date_publish'])
        except:
            continue

    # check that I don't already have it
    col_name = f"{_doc['date_publish'].year}-{_doc['date_publish'].month}-events"
    if bool(db[col_name].find_one({'_id':_doc['_id']})):
        continue

    if 'html' in _doc:
        del _doc['html']

    hold_ee.append(_doc)

    # process
    if len(hold_ee) >= 768:
        break
        process_docs(hold_ee)
        hold_ee = []
        count = 0

    count += 1

    # cut off if querying without finding anything
    if count > 30000:
        break

        
len([_doc for _doc in hold_ee if 'date_publish' not in _doc])

process_docs(hold_ee)
import pandas as pd
missing_date_dom = pd.Series([helpers.pull_domain(url) for url in missing_date])


# --------------------------------------------------------
# Other
# --------------------------------------------------------
# cursor = db['articles'].find(
#     {"eventExtracted":0, 'language':'en'}
# )
print('STARTING MULTILINGUAL')

model = ClassificationModel('xlmroberta'
                            , 'peacemachine/data/finetuned-transformers/XLMr-ModelOutput'
                            , num_labels=18
                            , args={
                                'n_gpu':1
                                , 'eval_batch_size':768})

cursor = db['articles'].find(
    {'language': {'$ne':'en'}}
).sort([('_id', -1)])

hold_ee = []
count = 0
for _doc in tqdm(cursor):

    if 'date_publish' not in _doc:
        missing_date.append(_doc['url'])
        continue

    if not _doc['date_publish']:
        missing_date.append(_doc['url'])
        continue

    if not isinstance(_doc['date_publish'], datetime):
        try:
            _doc['date_publish'] = parse(_doc['date_publish'])
        except:
            continue

    # make sure it's not in the collection already
    col_name = f"{_doc['date_publish'].year}-{_doc['date_publish'].month}-events"
    if bool(db[col_name].find_one({'_id':_doc['_id']})):
        continue

    if 'html' in _doc:
        del _doc['html']

    hold_ee.append(_doc)

    if len(hold_ee) >= 768:
        process_docs(hold_ee, language='ne')
        hold_ee = []
        count = 0
    
    count += 1

    # cut off if querying without finding anything
    if count > 30000:
        break

if len(hold_ee) > 0:
    process_docs(hold_ee)

