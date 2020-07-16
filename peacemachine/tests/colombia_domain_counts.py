import numpy as np
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from dateutil.parser import parse
from pymongo import MongoClient

db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p

with open('../data/domains/domains_Colombia.txt', 'r') as _file:
    colombia_domains = [ll.strip() for ll in _file.readlines()]

colombia_domains[0] = 'caracoltv.com'
colombia_domains[2] = 'canalrcn.com'

# date_counts = {}

# cursor = db.articles.find({'source_domain': domain})
# for _doc in tqdm(cursor):
#     d_down = parse(_doc['date_download']).replace(hour=0, minute=0, second=0, microsecond=0)
#     if d_down in date_counts:
#         date_counts[d_down] += 1
#     else:
#         date_counts[d_down] = 1

def domain_times(domain):
    """
    counts domain collections before/after split
    """
    before = 0
    after = 0

    cursor = db.articles.find({'source_domain': domain})
    for _doc in tqdm(cursor):
        try:
            if not isinstance(_doc['date_download'], datetime):
                try:
                    d_down = parse(_doc['date_download']).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
                except:
                    print('ERROR ON: ', _doc['date_download'])
                    continue
            else:
                d_down = _doc['date_download']
            if d_down <= datetime(2020, 4, 30).replace(tzinfo=None):
                before +=1
            else:
                after +=1
        except:
            print('ERROR!')
    
    return {'before': before, 'after': after}

df = pd.DataFrame()
for domain in colombia_domains:
    print(domain)
    counts = domain_times(domain)
    df.loc[domain, 'before'] = counts['before']
    df.loc[domain, 'after'] = counts['after']

