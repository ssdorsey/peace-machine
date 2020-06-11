import os 
import sys
from datetime import datetime
from dateutil.parser import parse
from tqdm import tqdm
from pymongo import MongoClient

if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@devlab-server').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p

num_changed = 0
for _doc in tqdm(db.events.find()):
    # first check if it has a date_publish
    if ('date' in _doc) and ('date_publish' not in _doc):
        _doc['date_publish'] = _doc['date']
        db.events.update_one(
            {
                '_id': _doc['_id']
            }, 
            {
                '$set': {'date_publish': _doc['date_publish']}
            }
        )
        num_changed += 1
    # then check to make sure it's a datetime object (for queries)
    if not isinstance(_doc['date_publish'], datetime):
        try:
            parsed_date = parse(_doc['date_publish'])
            db.events.update_one(
                {
                    '_id': _doc['_id']
                }, 
                {
                    '$set': {'date_publish': parsed_date}
                }
            )
            num_changed += 1
        except:
            pass
    # print an update on the num changed
    if (num_changed > 0) and (num_changed % 100 == 0):
        print('NUMBER CHANGED: ', num_changed)
