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

    count = 0

    for date in df.index:
        colname = f'articles-{date.year}-{date.month}'

        cur = db[colname].count_documents(
            {
                'source_domain': domain,
                'include': True,
                'civic1': {'$exists': True}
            }
        )
        count += cur

    return count


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

    count = 0

    for date in df.index:
        colname = f'articles-{date.year}-{date.month}'

        cur = db[colname].count_documents(
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
        
        count += cur

    return count


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
    total_local = 0
    total_international = 0

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
            
        loc_counts = p_umap(count_domain_loc, loc, [country_name]*len(loc), num_cpus=8)
        int_counts = p_umap(count_domain_int, ints, [country_name]*len(ints), num_cpus=8)

        print(f'local counts: {sum(loc_counts)}')
        print(f'international counts: {sum(int_counts)}')

        total_local += sum(loc_counts)
        total_international += sum(int_counts)

    print(f'Total local: {total_local}')
    print(f'Total international: {total_international}')


