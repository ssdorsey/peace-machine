#%%
import os 
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
import pandas as pd
import plotly.graph_objects as go

if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p

#%%
# load the data
df = pd.read_excel("/media/spenc/D1/Dropbox/ML for Peace/Data/Checking Event Data/"+
                    "Validation/procedure_1/Colombia_June2019_01.xlsx", sheet_name=1)

# df = pd.read_excel("D:/Dropbox/ML for Peace/Data/Checking Event Data/"+
#                     "Validation/procedure_1/Colombia_June2019_01.xlsx", sheet_name=1)

#%%
# check for each link
def check_link(link):
    art = db.articles.find_one({'url': {'$regex': f'^{link}'}})
    if bool(art):
        print(link)
        print('True')
        return True
    else:
        print(link)
        print('False')
        return False
        
new_found = [check_link(ll) for ll in tqdm(df['link'])]

# %%
# v619 = [_doc for _doc in 
#         db.articles.find({'source_domain':'vanguardia.com', 'date_publish': datetime(2019,6,1)})]

# %%
dates = pd.date_range(start=datetime(2019,1,1), end=datetime(2019,12,31))
vdf = pd.DataFrame({'date': dates})

vdf['vanguardia'] = [db.articles.count_documents({'date_publish': {'$gte': date, '$lt': date + pd.DateOffset(1)},
                     'source_domain': 'vanguardia.com'}) for date in tqdm(vdf['date'])]

vdf.head()

#%%
### check in the wayback urls
# Serkant/Diego data
el = pd.read_excel("/media/spenc/D1/Dropbox/ML for Peace/Data/Checking Event Data/Validation/procedure_1/colombia_elespectador_queryResults.xlsx", index_col=0)

# wayback urls
with open("/media/spenc/D1/Dropbox/peace-machine/peacemachine/data/wayback_urls/elespectador.com_urls.txt", 'r') as _file:
    el_wb = [ll.strip() for ll in _file.readlines()]
# drop the '/' at the end since it isn't in the diego/serkant urls

def check_el(url):
    # check to see if it's in the DB in any form
    if bool(db.articles.find_one({'url': url})) or bool(db.articles.find_one({'url': url+'/'})):
        return 'DB'
    # check to see if wayback has it
    matches = [uu for uu in el_wb if url.split('/')[-1] in uu]
    if len(matches) > 0:
        return 'Wayback'
    # check to see if it's in the missing date DB
    if bool(db['articles_nodate'].find_one({'url': url})) or bool(db['articles_nodate'].find_one({'url': url+'/'})):
        return 'DB-NoDate'
    return False

for _index in el.index:
    test_url = el.loc[_index, 'url']
    el.loc[_index, 'spencer_check'] = check_el(test_url)

# %%
# simple monthly graph of all counts
gdf = pd.DataFrame()
gdf['date'] = pd.date_range(start='2000-1-1', end='2020-7-1', freq='M')

for ii in gdf.index:
    date = gdf.loc[ii, 'date']
    collection = f'{date.year}-{date.month}-events'
    gdf.loc[ii, 'doc_count'] = db.command('collstats', collection)['count']

fig = go.Figure(data=go.Scatter(x=gdf['date'], y=gdf['doc_count']))
fig.show()


#%%
# graph a single month
def graph_daily(year, month):
    collection = f'{year}-{month}-events'
    ddf = pd.DataFrame()
    ddf['date'] = pd.date_range(
        start = f'{year}-{month}-1',
        end = f'{year}-{month+1}-1',
        freq='D'
    )
    for ii in ddf.index[:-1]:
        ddf.loc[ii, 'doc_count'] = db[collection].count_documents(
            {
                'date_publish': {
                    '$gte': ddf.loc[ii, 'date'],
                    '$lt': ddf.loc[ii+1, 'date']
                }
            }
        )
    # drop the last row (first day of next month)
    ddf = ddf.iloc[0:-1, :]

    fig = go.Figure(data=go.Scatter(x=ddf['date'], y=ddf['doc_count']))
    fig.show()

graph_daily(2020, 3)
graph_daily(2018, 9)

#%%
def graph_domains_day(year, month, day):
    collection = f'{year}-{month}-events'
    ddf = pd.DataFrame()
    ddf['domain'] = db[collection].distinct(
        key='source_domain', 
        filter={
                'date_publish': {
                    '$gte': datetime(year,month,day),
                    '$lt': datetime(year,month,day+1)
                }
        }
    )
    for ii in ddf.index:
        ddf.loc[ii, 'doc_count'] = db[collection].count_documents(
            {
                'date_publish': {
                    '$gte': datetime(year, month, day),
                    '$lt': datetime(year, month, day+1)
                }, 
                'source_domain': ddf.loc[ii, 'domain']
            }
        )

    fig = go.Figure(data=go.Bar(x=ddf['domain'], y=ddf['doc_count']))
    fig.show()

graph_domains_day(2020,3,1) # Problem with botasot.info
graph_domains_day(2018,9,21) # Problem with lusakatimes.com

#%%
# wtf is up with 2020-3-1? botasot.info

# db['2020-3-events'].count_documents(
#     {
#         'source_domain': 'botasot.info',
#         'url': {
#             '$not': {'$regex': r'^https:////www/.botasot/.info//arkiva///?from'}
#         }
#     }
# )

# res = db['2020-3-events'].delete_many(
#     {
#         'url': {'$regex': r'^https:////www/.botasot/.info//arkiva///?from'}
#     }
# )
# res.deleted_count

# wtf is up with 2018-9-21? lusakatimes.com AND archive.balkaninsight.com
# res = db['2018-9-events'].delete_many(
#     {
#         '_id': {'$ne': ObjectId('5e7b2516daeb6c6d7481b5ef')}, 
#         'title': 'Zambia is not in a debt crisis-World Bank'
#     }
# )

for _doc

#%%
# interactive graph of counts by source


