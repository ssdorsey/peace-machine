# fix the ones that news-please doesn't get
import re
from tqdm import tqdm
import ast
import numpy as np
import pandas as pd
import datetime
from peacemachine.event_builder import helpers
# from joblib import Parallel, delayed

# import htmlparsers

import pymongo
cl = pymongo.MongoClient()
db = cl.ml4p

# standardmedia.co.ke
# sunnewsonline.com
# mmtanzania.co.tz
# bbc.comm? 
# ft.com

# -----------------------------------------------------------------------
# old stories backup
# -----------------------------------------------------------------------
stories1 = pd.read_csv("D:\Dropbox\ML for Peace\Spencer_Code\Clean\Data\stories.csv")
stories2 = pd.read_csv("D:\Dropbox\ML for Peace\Spencer_Code\Clean\Data\stories2.csv")
stories = pd.concat([stories1, stories2])
stories['text'] = [ast.literal_eval(tt) for tt in stories['text']]
stories['text'] = [' '.join(tt) for tt in stories['text']]
stories['text'] = [' '.join(tt.strip('][').split(', '))[1:-1] for tt in tqdm(stories['text'])]

ep = pd.read_csv("D:\Dropbox\ML for Peace\Spencer_Code\Clean\Data\events_preliminary.csv")
fixed = [' '.join(tt.strip('][').split(', '))[1:-1] for tt in tqdm(ep['text'])]
ep['text'] = fixed

df = pd.concat([stories, ep])
df = df.drop([col for col in df.columns if col.startswith('Unnamed')], axis=1)
df = df.drop_duplicates(subset=['url'])

df = df[['title', 'text', 'date', 'url']]
df = df.rename({'text': 'maintext', 'date': 'date_publish'})

for row_num in tqdm(range(699609, len(df))):
    www = db.articles.count_documents({'url': f'https://www.{df["url"].iloc[row_num]}'})
    no_www = db.articles.count_documents({'url': f'https://{df["url"].iloc[row_num]}'})

    if (www + no_www) > 0:
        pass
    else:
        try:
            db.articles.insert_one(dict(df.iloc[row_num]))
        except:
            print('ERROR!')
            pass

for doc in tqdm(db.articles.find()):
    date_cond = 'date' in doc and 'date_publish' not in doc
    text_cond = 'text' in doc and 'maintext' not in doc
    if date_cond or text_cond:
        db.articles.update_one(
            {
                '_id': doc['_id']
            }, 
            {
                '$rename': {'text': 'maintext', 'date': 'date_publish'}
            }
        )

for doc in tqdm(db.events.find()):
    try:
        if isinstance(doc['date_publish'], datetime.datetime):
            continue
        new_date = helpers.parse_date(doc['date_publish'])
        up = db.events.update_one(
            {
                '_id': doc['_id']
            }, 
            {
                '$set': {'date_publish': new_date}
            }
        )
    except:
        print('ERROR')


# -----------------------------------------------------------------------
# Vanguard NGR fix
# -----------------------------------------------------------------------
vre = re.compile(r'^Kindly Share This Story:\n(By.*?\n)?')
def vanguardngrcom_fix(_doc):
    # fix the text
    fixed_text = vre.sub('', _doc['maintext'])
    # update the doc
    db.articles.update_one(
        {'_id': _doc['_id']},
        {'$set': {'maintext': fixed_text}}
    )
    # remove from the events collection
    db.events.remove({'_id': _doc['_id']})

for doc in tqdm(db.articles.find({'url': {'$regex': '^https?:\/\/(www\.)?vanguardngr.com'}})):
    vanguardngrcom_fix(doc)


db.articles.count_documents({'url': {'$regex': '^https?:\/\/(www\.)?(almizan\.info|aminiya\.dailytrust.com.ng|businessnews\.com.ng|sunnewsonline\.com|guardian\.ng|nationaldailyng\.com|thenewsnigeria\.com.ng|nan\.ng|tribuneonlineng\.com|punchng\.com|vanguardngr\.com|championnews\.com.ng|politicsngr\.com)'}})

nigeria = db.events.find({'bad_location':'Nigeria'})

future = [doc for doc in db.events.find({'bad_location':'Nigeria', 'date_publish':{'$regex': '^2020-06'}})]
change_election = [doc for doc in db.events.find({'bad_location': 'Nigeria', 'event_type':'changeelection'})]

no_loc = db.events.find(
    {'$or': [
        {'bad_location': ''},
        {'bad_location': np.nan}
    ]}
)

for _doc in tqdm(no_loc):
    if _doc['url'].startswith('http'):
        continue
    furl = _doc['url'].split('/')[0]
    if furl in helpers.domain_locs.keys():
        db.events.update_one(
            {
                '_id': _doc['_id']
            },
            {
                '$set': {'bad_location': helpers.domain_locs[furl]}
            }
        )

van = db.events.find({'url': {'$regex': '^vanguardngr'}})

for _doc in tqdm(db.events.find({'bad_location': 'Ecudaor'})):
    db.events.update_one(
        {
            '_id': _doc['_id']
        },
        {
            '$set': {'bad_location': 'Ecuador'}
        }
    )
