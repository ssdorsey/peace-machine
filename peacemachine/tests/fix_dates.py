import os 
import sys
from datetime import datetime
from dateutil.parser import ParserError
from dateutil.parser import parse
from tqdm import tqdm
from pymongo import MongoClient

if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@devlab-server').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p



def fix_dates(collection):
    num_changed = 0

    cursor = db[collection].find(
        {
            '$or': [
                {'date_publish': {'$exists': False}}, 
                {'date_publish': {'$not': {'$type': 'date'}}}
            ]
        }
    )

    for _doc in tqdm(cursor):
        # first check if it has a date_publish
        if ('date' in _doc) and ('date_publish' not in _doc):
            _doc['date_publish'] = _doc['date']
            # if it's already the right type, insert and continue
            if isinstance(_doc['date_publish'], datetime):
                db[collection].update_one(
                    {
                        '_id': _doc['_id']
                    }, 
                    {
                        '$set': {'date_publish': _doc['date_publish']}
                    }
                )
                num_changed += 1
                continue
        # if there's still so date_publish, dump it
        if ('date_publish' not in _doc) or (not _doc['date_publish']):
            db['articles_nodate'].insert_one(_doc)
            db[collection].delete_one({'_id':_doc['_id']})
            continue
        # then check to make sure it's a datetime object (for queries)
        if not isinstance(_doc['date_publish'], datetime):
            try:
                parsed_date = parse(_doc['date_publish'])
                db[collection].update_one(
                    {
                        '_id': _doc['_id']
                    }, 
                    {
                        '$set': {'date_publish': parsed_date}
                    }
                )
                num_changed += 1
            # if the parse doesn't work, drop the doc
            except ParserError:
                db['articles_nodate'].insert_one(_doc)
                db[collection].delete_one({'_id':_doc['_id']})

        # print an update on the num changed
        if (num_changed > 0) and (num_changed % 1000 == 0):
            print('NUMBER CHANGED: ', num_changed)

for col in db.list_collection_names():
    print('STARTING: ' + col)
