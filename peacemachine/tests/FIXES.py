"""
compilation of one-off fixes that I need to integrate into the overall workflow
"""
import sys
import os
import re
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from tqdm import tqdm

if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p


# -------------------------------------------------------------------------------------------
# archive.balkaninsight.com has bad dates, this fixes that
# TODO: integrate into the newsplease pipeline

date_regex = re.compile(r'-(\d{2}-\d{2}-(19|20)\d{2})')

def fix_events_archivebalkaninsightcom(collection):

    cursor = db[collection].find({'source_domain': 'archive.balkaninsight.com'})

    for _doc in cursor:
        try:
            # get the right date
            url_date = datetime.strptime(date_regex.search(_doc['url']).group(1), '%m-%d-%Y')
            # insert into the proper collection
            new_collection = f'{url_date.year}-{url_date.month}-events'
            if new_collection != collection:
                db[new_collection].insert_one(_doc)
                # remove from this one
                db[collection].delete_one({'_id': _doc['_id']})
        except AttributeError:
            pass

# fix the collections
event_collections = [col for col in db.list_collection_names() if col.endswith('-events')]
for col in tqdm(event_collections):
    fix_events_archivebalkaninsightcom(col)

# fix the articles
cursor = db.articles.find({'url': {'$regex': '^http://archive.balkaninsight.com'}})

for _doc in tqdm(cursor):
    try:
        url_date = datetime.strptime(date_regex.search(_doc['url']).group(1), '%m-%d-%Y')
        db.articles.update_one(
            {'_id': _doc['_id']}, 
            {
                '$set': {
                    'date_publish': url_date
                }
            }
        )
    except AttributeError:
        pass


# -------------------------------------------------------------------------------------------
# in this case there were like 2 millions versions of this article... 
# res = db['2018-9-events'].delete_many(
#     {
#         '_id': {'$ne': ObjectId('5e7b2516daeb6c6d7481b5ef')}, 
#         'title': 'Zambia is not in a debt crisis-World Bank'
#     }
# )

res = db['articles'].delete_many(
    {
        '_id': {'$ne': ObjectId('5e7b2516daeb6c6d7481b5ef')}, 
        'source_domain': 'lusakatimes.com',
        'title': 'Zambia is not in a debt crisis-World Bank'
    }
)



# -------------------------------------------------------------------------------------------
# problem with the botasot archive
# res = db['2020-3-events'].delete_many(
#     {
#         'url': {'$regex': r'^https:\/\/www\.botasot\.info\/arkiva\/\?from'}
#     }
# )
# res.deleted_count

res = db['articles'].delete_many(
    {
        'url': {'$regex': r'^https:\/\/www\.botasot\.info\/arkiva\/\?from'}
    }
)
res.deleted_count


# -------------------------------------------------------------------------------------------
# here's where I'll get all the urls and graph them
os.chdir('..')
from peacemachine.event_builder import helpers
domains = helpers.domain_locs
for ii in ['apnews.com','reuters.com','bbc.com','nytimes.com','washingtonpost.com','aljazeera.com','theguardian.com','dw.com','france24.com','bloomberg.com','ft.com','wsj.com','csmonitor.com','latimes.com','scmp.com','xinhuanet.com','news.yahoo.com']


