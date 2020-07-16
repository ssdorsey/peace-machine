import numpy as np
import pandas as pd
from urllib.parse import urlparse
from tqdm import tqdm
from pymongo import MongoClient

db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
events = db.events

# import work from Donald/Joan with the bad sections
sections = pd.read_excel('../data/domains/bad_sections.xlsx')
domains = set(sections['domain'])

# list the domains that have useful info
have_sections = set()
for ii in range(len(sections)):
    if sections.iloc[ii, 1:].isna().sum() != 17:
        have_sections.add(sections.loc[ii, 'domain'])

internationals = ['nytimes.com','washingtonpost.com','aljazeera.com','theguardian.com','dw.com','france24.com',
    'bloomberg.com','ft.com','wsj.com','csmonitor.com','latimes.com', 'scmp.com', 'xinhuanet.com']

# drop the comments
sections = sections.drop(labels=['Comment_section', 'comment_section2'], axis=1)

def pull_domain(url):
    """
    Pull the domain (without www.) from a url
    :param: string in url format
    :return: string of only domain
    """
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


def determine_exclude(_doc):
    """
    determines whether a certain doc should be excluded from counts
    :param _doc: pymongo document
    """
    if 'source_domain' not in _doc:
        _doc['source_domain'] = pull_domain('_doc')

    # see if it's from a domain I want
    if _doc['source_domain'] not in domains:
        return True

    # if I have no new info, move along
    if _doc['source_domain'] not in have_sections:
        return False

    # everything left will have something to use
    site_row = sections[sections['domain'] == _doc['source_domain']].iloc[0, 1:]

    # exclude editorial/opinion
    ops = [site_row[ii] for ii in site_row.index if ii.startswith('opinion_') and not pd.isna(site_row[ii])]
    for pat in ops:
        if pat in _doc['url']:
            return True

    # internationals with sections, use only international

    if _doc['source_domain'] in internationals:
        news = [site_row[ii] for ii in site_row.index if ii.startswith('international_') and not pd.isna(site_row[ii])]
    else:
        # if I have news sections, use only those
        news = [site_row[ii] for ii in site_row.index if ii.startswith('news_') and not pd.isna(site_row[ii])]
    
    if not any([pat in _doc['url'] for pat in news]):
        return True

    # if I make it this far, no need to exlude
    return False


def exclude_section(col):
    """
    adds an "exclude" field for each document in a collection according to the url filters in bad_sections.xlsx
    :param col: string, collection name
    """

    cursor = db[col].find({'exclude': {'$exists': False}})

    for _doc in tqdm(cursor):
        # try:
        res = determine_exclude(_doc)
        db[col].update_one({'_id': _doc['_id']}, {'$set': {'exclude': res}})
        # except:
            # print('ERROR! ERROR!')


collections = [col for col in db.list_collection_names() if col.endswith('-events')]
collections += ['lac']

for collection in collections:
    exclude_section(collection)
