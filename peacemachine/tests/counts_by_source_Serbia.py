import os
import re
import pandas as pd
from tqdm import tqdm
from p_tqdm import p_umap
import time

from pymongo import MongoClient

db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p

countries = ['SRB']

ints = [doc['source_domain'] for doc in db['sources'].find({'major_international': True, 'include': True})]
loc = [doc['source_domain'] for doc in db['sources'].find(
    {
        'primary_location': {'$in': ['SRB']},
        'include': True
    }
)]
domains = ints+loc

events = [k for k in db.models.find_one({'model_name': 'civic1'}).get('event_type_nums').keys()] + ['-999']

legal_re = re.compile(r'(freedom.*|assembl.*|associat.*|term limit.*|independen.*|succession.*|demonstrat.*|crackdown.*|draconian|censor.*|authoritarian|repress.*|NGO|human rights)')


def check_legal(doc):
    try:
        if bool(legal_re.search(doc.get('title'))) or bool(legal_re.search(doc.get('maintext'))):
            return True
        else:
            return False
    except:
        return False


country_re = re.compile(r'Serbia')

df = pd.DataFrame()
df['date'] = pd.date_range('2000-1-1', '2020-12-1', freq='M')
df.index = df['date']
df['year'] = [dd.year for dd in df.index]
df['month'] = [dd.month for dd in df.index]

for et in events:
    df[et] = [0] * len(df)


# START WITH THE LOCALS
def count_domain_loc(domain):

    db2 = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p

    # create a new frame to work with
    dom_df = df.copy(deep=True)

    for date in dom_df.index:
        colname = f'articles-{date.year}-{date.month}'

        cur = db2[colname].find(
            {
                'source_domain': domain,
                'include': True,
                'civic1': {'$exists': True}
            }
        )
        docs = [doc for doc in cur]

        for et in events:
            # TODO: APPLY THE LEGALCHANGE FILTER!![dd.year for dd in df['date']]

            if et == 'legalchange':
                sub_docs = [doc for doc in docs if doc['civic1']['event_type'] == 'legalchange']
                sub_docs = [doc for doc in sub_docs if check_legal(doc)]
                count = len(sub_docs)

            else: 
                count = len([doc for doc in docs if doc['civic1']['event_type'] == et])

            dom_df.loc[date, et] = count

    dom_df.to_csv(f'D:Dropbox/ML for Peace/Counts_Civic/2020_12_1/{domain}.csv')



# Then ints
def count_domain_int(domain):

    db2 = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p

    # create a new frame to work with
    dom_df = df.copy(deep=True)

    for date in dom_df.index:
        colname = f'articles-{date.year}-{date.month}'

        cur = db2[colname].find(
            {
                'source_domain': domain,
                'include': True,
                'civic1': {'$exists': True},
                '$or': [
                    {'title': {'$regex': 'Serbia'}},
                    {'maintext': {'$regex': 'Serbia'}}
                ]
            }
        )
        docs = [doc for doc in cur]

        for et in events:
            # TODO: APPLY THE LEGALCHANGE FILTER!![dd.year for dd in df['date']]

            if et == 'legalchange':
                sub_docs = [doc for doc in docs if doc['civic1']['event_type'] == 'legalchange']
                sub_docs = [doc for doc in sub_docs if check_legal(doc)]
                count = len(sub_docs)

            else: 
                count = len([doc for doc in docs if doc['civic1']['event_type'] == et])

            dom_df.loc[date, et] = count

    dom_df.to_csv(f'D:Dropbox/ML for Peace/Counts_Civic/2020_12_1/{domain}_serbia.csv')

if __name__ == "__main__":
    
    p_umap(count_domain_loc, loc, num_cpus=8)
    p_umap(count_domain_int, ints, num_cpus=8)


