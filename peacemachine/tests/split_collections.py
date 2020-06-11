import os 
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from pymongo import MongoClient

if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p


def monthly_collection(month_start):
    """
    creates a mongodb collection of all documents within a certain month
    :param month: datetime, start of the month ex: datetime(2000,1,1)
    """
    ### create collection
    col_name = f'{month_start.year}-{month_start.month}-events'
    if col_name not in db.list_collection_names():
        db[col_name].create_index('date_publish')
        db[col_name].create_index('bad_location')
        db[col_name].create_index('event_type')
        db[col_name].create_index('url', unique=True)

    ### add data
    month_cursor =  db.events.find(
            {
                'date_publish': {'$gte': month_start, '$lt': month_start+relativedelta(months=1)}
            }
        )
    # cut data I don't want
    keep_keys = {'_id', 'url', 'bad_location', 'date_publish', 'domain', 'event_type', 'model_outputs', 
                    'model_max', 'exclude', 'title'}

    month_docs = []
    for _doc in month_cursor:
        _doc = {k:v for k,v in _doc.items() if k in keep_keys}
        month_docs.append(_doc)
    
    # insert to new collection
    if len(month_docs) > 0:
        res = db[col_name].insert_many(month_docs)

month_starts = []
date = datetime(2000, 1, 1)
while date < (datetime.today() - relativedelta(months=1)):
    month_starts.append(date)
    date += relativedelta(months=1)

for ms in tqdm(month_starts):
    monthly_collection(ms)
