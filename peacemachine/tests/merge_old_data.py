"""
This is a script to insert the old data that once was lost but now is found
"""
from tqdm import tqdm
from urllib.parse import urlparse
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

rm = MongoClient("mongodb://ml4pAdmin:ml4peace@devlab-server")
rdb = rm.ml4p
rdb.articles.find_one()

lc = MongoClient()
ldb = lc.ml4p
ldb.articles.find_one() 

def strip_url(url):
    """
    strips a url of all the fluff
    """
    parsed = urlparse(url)
    sturl = parsed.netloc + parsed.path
    # strip www.
    sturl = sturl.replace('www.', '')
    return sturl


# ----------------------------------------
# insert "articles" collection
# ----------------------------------------
print('STARTING ARTICLES')

art_cursor = ldb.articles.find({'in_new_db': False})

for _doc in tqdm(art_cursor):
    # drop fields I don't want
    _doc.pop('_id', None)
    _doc.pop('in_new_db', None)
    # get the stripped URL
    _doc['stripped_url'] = strip_url(_doc['url'])
    # insert into new 
    try:
        io = rdb.articles.insert_one(_doc)
    except DuplicateKeyError:
        pass

# ----------------------------------------
# insert "events" collection
# ----------------------------------------
print('STARTING EVENTS')

eve_cursor = ldb.events.find({'in_new_db': False})

for _doc in tqdm(eve_cursor):
    # drop fields I don't want
    _doc.pop('_id', None)
    _doc.pop('in_new_db', None)
    _doc.pop('bad_location', None)
    _doc.pop('event_type', None)
    _doc.pop('model_outputs', None)
    _doc.pop('model_max', None)
    # get the stripped url
    _doc['stripped_url'] = strip_url(_doc['url'])
    # insert into new
    try:
        io = rdb.articles.insert_one(_doc)
    except DuplicateKeyError:
        pass

# ----------------------------------------
# insert "serbia" collection
# ----------------------------------------
print('STARTING SERBIA')

serbia_cursor = ldb.serbia.find({'in_new_db': False})

for _doc in tqdm(serbia_cursor):
    # drop fields I don't want
    _doc.pop('_id', None)
    _doc.pop('in_new_db', None)
    _doc.pop('BERT_class', None)
    _doc.pop('BERT_class_num', None)
    _doc.pop('BERT_max', None)
    _doc.pop('translated', None)
    # get the stripped url
    _doc['stripped_url'] = strip_url(_doc['url'])
    # insert into new
    try:
        io = rdb.articles.insert_one(_doc)
    except DuplicateKeyError:
        pass
