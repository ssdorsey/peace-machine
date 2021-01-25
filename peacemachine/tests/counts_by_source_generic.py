import os
from pathlib import Path
import re
import pandas as pd
from tqdm import tqdm
from p_tqdm import p_umap
import time

from pymongo import MongoClient

db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p

today = pd.Timestamp.now()

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


# START WITH THE LOCALS
def count_domain_loc(domain, country_name):

    # db2 = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p

    df = pd.DataFrame()
    df['date'] = pd.date_range('2000-1-1', today + pd.Timedelta(31, 'd') , freq='M')
    df.index = df['date']
    df['year'] = [dd.year for dd in df.index]
    df['month'] = [dd.month for dd in df.index]

    for et in events:
        df[et] = [0] * len(df)

    for date in df.index:
        colname = f'articles-{date.year}-{date.month}'

        cur = db[colname].find(
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

            df.loc[date, et] = count

    # check if directory exists
    path = f'D:\\Dropbox\\ML for Peace\\Counts_Civic\\{today.year}_{today.month}_{today.day}\\{country_name}\\'
    if not os.path.exists(path):
        Path(path).mkdir(parents=True, exist_ok=True)

    df.to_csv(path + f'{domain}.csv')


# Then ints
def count_domain_int(domain, country_name):

    # db2 = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p

    df = pd.DataFrame()
    df['date'] = pd.date_range('2000-1-1', today + pd.Timedelta(31, 'd') , freq='M')
    df.index = df['date']
    df['year'] = [dd.year for dd in df.index]
    df['month'] = [dd.month for dd in df.index]

    for et in events:
        df[et] = [0] * len(df)

    for date in df.index:
        colname = f'articles-{date.year}-{date.month}'

        cur = db[colname].find(
            {
                'source_domain': domain,
                'include': True,
                'civic1': {'$exists': True},
                '$or': [
                    {'title': {'$regex': country_name}},
                    {'maintext': {'$regex': country_name}}
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

            df.loc[date, et] = count

    path = f'D:\\Dropbox\\ML for Peace\\Counts_Civic\\{today.year}_{today.month}_{today.day}\\{country_name}\\'
    if not os.path.exists(path):
        Path(path).mkdir(parents=True, exist_ok=True)

    df.to_csv(path + f'{domain}.csv')

if __name__ == "__main__":

    countries = [
        ('Albania', 'ALB'),
        ('Benin', 'BEN'),
        ('Colombia', 'COL'),
        ('Ecuador', 'ECU'),
        ('Ethiopia', 'ETH'),
        ('Georgia', 'GEO'),
        ('Kenya', 'KEN'),
        ('Paraguay', 'PRY'),
        ('Mali', 'MLI'),
        ('Morocco', 'MAR'),
        ('Nigeria', 'NGA'),
        ('Serbia', 'SRB'),
        ('Senegal', 'SEN'),
        ('Tanzania', 'TZA'),
        ('Uganda', 'UGA'),
        ('Ukraine', 'UKR'),
        ('Zimbabwe', 'ZWE'),
    ]


    # Bangladesh, Bolivia, Bosnia, Cambodia, CAR, DRC, El Salvador, Ghana, Guatemala, Honduras, Hungary, India, Indonesia, Iraq, Jamaica, Jordan, Kazakhstan, Liberia, Libya, Malawi, Malaysia, Mexico, Mongolia, Mozambique, Myanmar, Nepal, Nicaragua, Niger, Pakistan, Philippines, Rwanda, South Africa, South Sudan, Thailand, Yemen

    for ctup in countries:

        print('Starting: '+ctup[0])

        country_name = ctup[0]
        country_code = ctup[1]

        loc = [doc['source_domain'] for doc in db['sources'].find(
            {
                'primary_location': {'$in': [country_code]},
                'include': True
            }
        )]
        ints = [doc['source_domain'] for doc in db['sources'].find({'major_international': True, 'include': True})]
            
        p_umap(count_domain_loc, loc, [country_name]*len(loc), num_cpus=8)
        p_umap(count_domain_int, ints, [country_name]*len(ints), num_cpus=8)


