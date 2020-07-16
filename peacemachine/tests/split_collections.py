import os 
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
from peacemachine.event_builder import helpers

if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p


# def monthly_collection(month_start):
#     """
#     creates a mongodb collection of all documents within a certain month
#     :param month: datetime, start of the month ex: datetime(2000,1,1)
#     """
#     ### create collection
#     col_name = f'{month_start.year}-{month_start.month}-events'
#     if col_name not in db.list_collection_names():
#         db[col_name].create_index('date_publish')
#         db[col_name].create_index('bad_location')
#         db[col_name].create_index('event_type')
#         db[col_name].create_index('exclude')
#         db[col_name].create_index('source_domain')
#         db[col_name].create_index('url', unique=True)

#     ### add data
#     month_cursor =  db.events.find(
#             {
#                 'date_publish': {'$gte': month_start, '$lt': month_start+relativedelta(months=1)}
#             }
#         )
#     # cut data I don't want
#     keep_keys = {'_id', 'url', 'bad_location', 'date_publish', 'domain', 'event_type', 'model_outputs', 
#                     'model_max', 'exclude', 'title'}

#     month_docs = []
#     for _doc in month_cursor:
#         _doc = {k:v for k,v in _doc.items() if k in keep_keys}
#         month_docs.append(_doc)
    
#     # insert to new collection
#     if len(month_docs) > 0:
#         res = db[col_name].insert_many(month_docs)

# month_starts = []
# date = datetime(2000, 1, 1)
# while date < (datetime.today() - relativedelta(months=1)):
#     month_starts.append(date)
#     date += relativedelta(months=1)

# for ms in tqdm(month_starts):
#     monthly_collection(ms)

# month_collections = [col for col in db.list_collection_names() if col.endswith('-events')]
# for col_name in month_collections:
#     indexes = db[col_name].index_information()
#     index_names = [v['key'][0][0] for v in indexes.values()]
#     if 'url' not in index_names:
#         db[col_name].create_index('url', unique=True)
#     for index in ['date_publish', 'bad_location', 'event_type', 'exclude']:
#         if index not in index_names:
#             db[col_name].create_index(index)

# month_collections = sorted([col for col in db.list_collection_names() if col.endswith('-events')])
# for collection in tqdm(month_collections):
#     db[collection].create_index('source_domain')

# month_collections = sorted([col for col in db.list_collection_names() if col.endswith('-events')])
# for col_name in month_collections:
#     print('STARTING: ' + col_name)
    
#     cursor = db[col_name].find({'domain': {'$exists': True}, 'source_domain': {'$exists': False}})

#     for _doc in tqdm(cursor):
#         db[col_name].update_one(
#             {'_id': _doc['_id']}, 
#             {
#                 '$set': {
#                     'source_domain': _doc['domain']
#                 }
#             }
#         )
    
#     db[col_name].update_many({}, {'$unset': {'domain':1}})

#     cursor = db[col_name].find({'url': {'$exists': True}, 'source_domain': {'$exists': False}})

#     for _doc in tqdm(cursor):
#         db[col_name].update_one(
#             {'_id': _doc['_id']}, 
#             {
#                 '$set': {
#                     'source_domain': helpers.pull_domain(_doc['url'])
#                 }
#             }
#         )
    


### standardize bad_location to None
# month_collections = [col for col in db.list_collection_names() if col.endswith('-events')]

# for col_name in tqdm(month_collections):
#     cursor = db[col_name].find({'bad_location': np.nan})
#     db[col_name].update_many(
#         {
#             'bad_location': ''
#         }, 
#         {
#             '$set': {'bad_location': None}
#         }
#     )

### fix bad_location
# month_collections = sorted([col for col in db.list_collection_names() if col.endswith('-events')])

# updated_count = 0 
# for col_name in tqdm(month_collections):
#     print(f'Starting {col_name}')
#     cursor = db[col_name].find({'bad_location': None})
#     for _doc in cursor:
#         cut_domain = '.'.join(_doc['source_domain'].split('.')[1:])
#         if cut_domain in helpers.domain_locs:
#             db[col_name].update_one(
#                 {'_id': _doc['_id']}, 
#                 {
#                     '$set': {'bad_location': helpers.domain_locs[cut_domain]}
#                 }
#             )
#             updated_count += 1
#             if updated_count % 100 == 0:
#                 print(f'Updated count: {updated_count}')

# ### fix the source_domains TODO: integrate this into newsplease
# def fix_sourcedomain(collection):
#     sd_cursor = db[collection].find({'source_domain': {'$regex': '^www.'}}).batch_size(1000)
#     for _doc in tqdm(sd_cursor):
#         db[collection].update_one(
#             {'_id': _doc['_id']}, 
#             {
#                 '$set': {'source_domain': _doc['source_domain'][4:]}
#             }
#         )

# print('NOW FIXING SOURCE_DOMAIN')
# for col in db.list_collection_names():
#     print('SOURCE_DOMAIN: ', col)
#     fix_sourcedomain(col)


def deduplify_day_title_source(collection):

    del_count = 0

    cursor = db[collection].find(no_cursor_timeout=True)

    for _doc in tqdm(cursor):
        # count_identical = db[collection].count_documents(
        #     {
        #         'date_publish': _doc['date_publish'],
        #         'title': _doc['title'],
        #         'source_domain': _doc['source_domain']
        #     }
        # )

        # if count_identical > 1:
        res = db[collection].delete_many(
            {
                '_id': {'$ne': _doc['_id']},
                'date_publish': _doc['date_publish'],
                'source_domain': _doc['source_domain'],
                'title': _doc['title']
            }
        )
        if res.deleted_count > 0: 
            del_count += res.deleted_count
            # print(f'DELETED THIS DOC: {res.deleted_count}')
            # print(f'TOTAL DELETED: {del_count}')

    cursor.close()

# month_collections = sorted([col for col in db.list_collection_names() if col.endswith('-events')])
month_collections = ['2020-3-events', '2019-9-events']
for col_name in month_collections:
    print('STARTING DAY_TITLE_SOURCE DEDUPLIFICATION: ' + col_name)
    try:
        deduplify_day_title_source(col_name)
    except:
        pass

# deduplify_day_title_source('articles')
