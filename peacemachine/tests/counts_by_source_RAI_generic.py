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

events = [k for k in db.models.find_one({'model_name': 'RAI'}).get('event_type_nums').keys()] + ['-999']

russia = pd.read_excel(r"data\actors\Acronyms_Russia.xlsx")
# russia_re = '(' + '|'.join(russia['CompanyName']) + ')'

china = pd.read_excel(r"data\actors\Acronyms_China.xlsx")
china['CompanyName'] = china['CompanyName'].str.strip()
# china_re = '(' + '|'.join(china['CompanyName']) + ')'

rai_re = '(' + '|'.join(pd.concat([russia['CompanyName'], china['CompanyName']])) + ')'


# START WITH THE LOCALS
def count_domain_loc(domain, country_name):

    # create a new frame to work with
    df = pd.DataFrame()
    df['date'] = pd.date_range('2000-1-1', '2020-12-1', freq='M')
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
                'RAI': {'$exists': True}, 
                '$or': [
                    {'title': {'$regex': rai_re}},
                    {'maintext': {'$regex': rai_re}}
                ]
            }
        )
        docs = [doc for doc in cur]

        for et in events:
            # TODO: APPLY THE LEGALCHANGE FILTER!![dd.year for dd in df['date']]

            count = len([doc for doc in docs if doc['RAI']['event_type'] == et])

            df.loc[date, et] = count

    path = f'D:\\Dropbox\\ML for Peace\\Counts_RAI\\{today.year}_{today.month}_{today.day}\\{country_name}\\'
    if not os.path.exists(path):
        Path(path).mkdir(parents=True, exist_ok=True)

    df.to_csv(path + f'{domain}.csv')



# Then ints
def count_domain_int(domain, country_name):

    # create a new frame to work with
    df = pd.DataFrame()
    df['date'] = pd.date_range('2000-1-1', '2020-12-1', freq='M')
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
                'RAI': {'$exists': True},
                '$and': [
                    {'$or': [
                        {'title': {'$regex': country_name}},
                        {'maintext': {'$regex': country_name}}
                    ]},
                   { '$or': [
                        {'title': {'$regex': rai_re}},
                        {'maintext': {'$regex': rai_re}}
                    ]}
                ]                
            }
        )
        docs = [doc for doc in cur]

        for et in events:
            # TODO: APPLY THE LEGALCHANGE FILTER!![dd.year for dd in df['date']]

            count = len([doc for doc in docs if doc['RAI']['event_type'] == et])

            df.loc[date, et] = count

    path = f'D:\\Dropbox\\ML for Peace\\Counts_RAI\\{today.year}_{today.month}_{today.day}\\{country_name}\\'
    if not os.path.exists(path):
        Path(path).mkdir(parents=True, exist_ok=True)

    df.to_csv(path + f'{domain}.csv')

if __name__ == "__main__":

    countries = [
        # ('Albania', 'ALB'),
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


    for ctup in countries:

        print('Starting: '+ ctup[0])

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
