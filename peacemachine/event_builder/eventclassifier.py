# 
from tqdm import tqdm
from joblib import Parallel, delayed
from simpletransformers.classification import ClassificationModel
import numpy as np

# from peacemachine.event_builder import helpers
import helpers

import pymongo
client = pymongo.MongoClient('mongodb://ml4pAdmin:ml4peace@localhost')
db = client.ml4p

model = ClassificationModel('roberta'
                            , 'data/finetuned-transformers/ModelOutput'
                            , num_labels=18
                            , args={
                                'n_gpu':1
                                , 'eval_batch_size':768})

# model = ClassificationModel('xlmroberta'
#                             , 'data/finetuned-transformers/XLMr-ModelOutput'
#                             , num_labels=18
#                             , args={
#                                 'n_gpu':1
#                                 , 'eval_batch_size':768})

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

error_urls = []

def process_docs(list_docs, language='en'):
    """
    processes list of docs and returns extracted events
    """
    inserted_count = 0
    list_docs = Parallel(n_jobs=-2)(delayed(helpers.build_combined)(doc) for doc in list_docs)

    list_docs = [dd for dd in list_docs if 'combined' in dd and dd['combined']]

    list_docs = [dd for dd in list_docs if isinstance(dd, str)]
    # get the domain
    for doc in list_docs:
        doc['domain'] = helpers.pull_domain(doc['url'])

    # get the location
    if language == 'en':
        bad_locations = Parallel(n_jobs=-2)(delayed(helpers.pull_country)(doc['combined']) for doc in list_docs)
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

    # TODO: REMOVE!! ONLY TEMP TO FILTER STORIES
    # list_docs = [doc for doc in list_docs if doc['bad_location'] in {'Kenya', 'Nigeria', 'Mali', 'Tanzania', 'Serbia', 'Georgia', 'Ecuador', 'Colombia'}]

    # do the predictions
    preds, model_outputs = model.predict([doc['combined'] for doc in list_docs])
    # modify outputs
    model_max = [float(max(mo)) for mo in model_outputs]
    event_types = [label_dict[ii] for ii in preds]

    for ii in range(len(model_max)):
        if model_max[ii] < 7:
            event_types[ii] = '-999'

    # return to database
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
    for doc in list_docs:
        try:
            db.events.insert_one(doc)
            inserted_count += 1
        except:
            error_urls.append(doc['url'])
            pass
    print(f'inserted_count: {inserted_count}')
    print(f'error count: {len(error_urls)}')

# --------------------------------------------------------
# ENGLISH
# --------------------------------------------------------
# cursor = db['articles'].find(
#     {'eventExtracted':0, 'language':'en'}
# ) 
print('STARTING ENGLISH')
cursor = db['articles'].find().skip(39000000)

missing_date = []
hold_ee = []
for _doc in tqdm(cursor):

    if 'language' in _doc:
        if _doc['language'] != 'en':
            continue

    if not _doc['date_publish']:
        missing_date.append(_doc['url'])
        continue

    if db.events.find_one({'_id':_doc['_id']}):
        continue

    if 'html' in _doc:
        del _doc['html']

    hold_ee.append(_doc)

    if len(hold_ee) >= 10000:
        process_docs(hold_ee)
        hold_ee = []
        # break

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
                            , 'data/finetuned-transformers/XLMr-ModelOutput'
                            , num_labels=18
                            , args={
                                'n_gpu':1
                                , 'eval_batch_size':768})

cursor = db['articles'].find(
    {'language': {'$ne':'en'}}
) 

hold_ee = []
for _doc in tqdm(cursor):

    if not _doc['date_publish']:
        continue

    # if not _doc['date_publish'].year==2020: # TODO: GET RID OF THIS!!! TEMPORARY!!!
    #     continue

    if db.events.find_one({'_id':_doc['_id']}):
        continue

    if 'html' in _doc:
        del _doc['html']

    hold_ee.append(_doc)

    if len(hold_ee) >= 10000:
        process_docs(hold_ee, language='ne')
        hold_ee = []
process_docs(hold_ee)

