import numpy as np
import pandas as pd
from urllib.parse import urlparse
from tqdm import tqdm
from pymongo import MongoClient

db = MongoClient('mongodb://ml4pAdmin:ml4peace@devlab-server').ml4p
events = db.events

# import work from Donald/Joan with the bad sections
sections = pd.read_excel('../data/domains/bad_sections.xlsx')
domains = set(sections['domain'])

# list the domains that have useful info
have_sections = set()
for ii in range(len(sections)):
    if sections.iloc[ii, 1:].isna().sum() != 17:
        have_sections.add(sections.loc[ii, 'domain'])

# drop the comments
sections = sections.drop(labels=['Comment_section', 'comment_section2'], axis=1)

# loop through each record... how fun this will be

cursor = events.find()

for _doc in tqdm(cursor):
    try:
        # see if it's from a domain I want
        if _doc['domain'] not in domains:
            # update
            events.update_one({'_id': _doc['_id']}, {'$set': {'exclude': True}})
            # move to next doc
            continue

        # if I have no new info, move along
        if _doc['domain'] not in have_sections:
            continue

        # everything left will have something to use
        site_row = sections[sections['domain'] == _doc['domain']].iloc[0, 1:]

        # exclude editorial/opinion
        ops = [site_row[ii] for ii in site_row.index if ii.startswith('opinion_') and not pd.isna(site_row[ii])]
        for pat in ops:
            if pat in _doc['url']:
                events.update_one({'_id': _doc['_id']}, {'$set': {'exclude': True}})

        # if I have news/international sections, use only those
        news = [site_row[ii] for ii in site_row.index if (ii.startswith('news_') or 
                ii.startswith('international_')) and not pd.isna(site_row[ii])]
        
        if not any([pat in _doc['url'] for pat in news]):
            events.update_one({'_id': _doc['_id']}, {'$set': {'exclude': True}})
        # if I make it this far, no need to exlude
        db.lac.update_one({'_id': _doc['_id']}, {'$set': {'exclude': False}})
    except:
        print('ERROR! ERROR!')

# def pull_domain(url):
#     """
#     Pull the domain (without www.) from a url
#     :param: string in url format
#     :return: string of only domain
#     """
#     domain = urlparse(url).netloc
#     if domain.startswith('www.'):
#         domain = domain[4:]
#     return domain


# cursor = db.lac.find()

# for _doc in tqdm(cursor):
#     # try:
#     # see if it's from a domain I want
#     _doc['domain'] = pull_domain(_doc['url'])
#     if _doc['domain'] not in domains:
#         # update
#         db.lac.update_one({'_id': _doc['_id']}, {'$set': {'exclude': True}})
#         # move to next doc
#         continue

#     # if I have no new info, move along
#     if _doc['domain'] not in have_sections:
#         continue

#     # everything left will have something to use
#     site_row = sections[sections['domain'] == _doc['domain']].iloc[0, 1:]

#     # exclude editorial/opinion
#     ops = [site_row[ii] for ii in site_row.index if ii.startswith('opinion_') and not pd.isna(site_row[ii])]
#     for pat in ops:
#         if pat in _doc['url']:
#             db.lac.update_one({'_id': _doc['_id']}, {'$set': {'exclude': True}})
#             continue
    
#     # internationals with sections, use only international
#     internationals = ['nytimes.com','washingtonpost.com','aljazeera.com','theguardian.com','dw.com','france24.com','bloomberg.com','ft.com','wsj.com','csmonitor.com','latimes.com']
#     if _doc['domain'] in internationals:
#         news = [site_row[ii] for ii in site_row.index if ii.startswith('international_') and not pd.isna(site_row[ii])]
#     else:
#         # if I have news sections, use only those
#         news = [site_row[ii] for ii in site_row.index if ii.startswith('news_') and not pd.isna(site_row[ii])]
    
#     if not any([pat in _doc['url'] for pat in news]):
#         db.lac.update_one({'_id': _doc['_id']}, {'$set': {'exclude': True}})
#         continue

#     # if I make it this far, no need to exlude
#     db.lac.update_one({'_id': _doc['_id']}, {'$set': {'exclude': False}})
    
# # except:
#     #     print('ERROR! ERROR!')

