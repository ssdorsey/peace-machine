"""
First cut at creating LAC RAI counts with Ecuador/Colombia and Russia/China
"""
### setup workspace
import os
import sys
import re
import pickle
from datetime import datetime
from tqdm import tqdm
from urllib.parse import urlparse
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
from pymongo import MongoClient
import spacy

nlp_en = spacy.load('en_core_web_sm')
nlp_es = spacy.load('es_core_news_sm')

if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@devlab-server').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p

### data info 
label_dict = pickle.load( open( "../data/LAC/label_dict.p", "rb" ) )
e_types = list(label_dict.keys())

with open('../data/domains/domains_Ecuador.txt', 'r') as _file:
    ecuador_domains = [dd.strip() for dd in _file.readlines()]
with open('../data/domains/domains_Colombia.txt', 'r') as _file:
    colombia_domains = [dd.strip() for dd in _file.readlines()]
with open('../data/domains/domains_international.txt', 'r') as _file:
    international_domains = [dd.strip() for dd in _file.readlines()]

ecuador_re = re.compile(r'(ecuador|ecuadorian)', re.IGNORECASE)
colombia_re = re.compile(r'(colombia)', re.IGNORECASE)

### helper functions
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


### query framework
month_starts = []
date = datetime(2000, 1, 1)
while date < (datetime.today() - relativedelta(months=1)):
    date += relativedelta(months=1)
    month_starts.append(date)


def filter_candidates(_doc, country):
    """
    filters out a list of documents for candiates that meet the search criteria
    """
    ### get the components
    art = db.articles.find_one({'url': _doc['url']})
    title = art['title']
    maintext = art['maintext']
    if not maintext:
        maintext = ''
    domain = pull_domain(_doc['url'])

    # check for Russia / China in title OR maintext
    cr_re = re.compile(r'(china|chinese|chino|russia|russian|rusia|ruso|rusa)', re.IGNORECASE)
    if not bool(cr_re.search(title)) or bool(cr_re.search(maintext)):
        return False

    # check for Ecuador / Colombia in title OR first 500 characters
    # cr_re = re.compile(r'(ecuador|ecuadorian|ecuatorian|colombia|colombian)', re.IGNORECASE)
    # if not bool(cr_re.search(title)) or bool(cr_re.search(maintext[:500])):
    #     return False

    # check that the story isn't about Venezuela (many slip through...)
    vene_re = re.compile(r'(nicolás maduro|juan guaidó|hugo chávez|venezuela)', re.IGNORECASE)
    if bool(vene_re.search(title)):
        return False
    
    # TODO: check that some other country isn't the real focus

    # to make sure we're in the right country, use names from internationals and domains
    if country.lower() == 'ecuador':
        if domain in colombia_domains:
            return False
        # must mention ecuador in early text for these
        if domain in international_domains:
            if not bool(ecuador_re.search(title)) or bool(ecuador_re.search(maintext[:500])):
                return False

    if country.lower() == 'colombia':
        if domain in ecuador_domains:
            return False
        # must mention ecuador in early text for these
        if domain in international_domains:
            if not bool(colombia_re.search(title)) or bool(colombia_re.search(maintext[:500])):
                return False

    # if pass filters, return true
    return True
    

# m_start = datetime(2019, 9, 1, 0, 0)
# e_type = 'diplomatic_visit'
# country = 'Colombia'

def monthly_counts_flat(country):
    hold_country = []

    for m_start in tqdm(month_starts):
        hold_series = pd.Series()
        hold_series['year'] = m_start.year
        hold_series['month'] = m_start.month
        hold_series['location'] = country

        for e_type in e_types:
            # get the date / event_type candidates
            cursor = db.lac.find(
                {   
                    'event_type': e_type,
                    'date_publish': {'$gte': m_start, '$lt': m_start+relativedelta(months=1)},
                    # 'exclude': {'$ne': True},
                }
            )
            candidates = [_doc for _doc in cursor]

            filter_res = [filter_candidates(candidate, country) for candidate in candidates]

            cut_candidates = [candidate for nn, candidate in enumerate(candidates) if filter_res[nn]]
            
            hold_series[e_type] = len(cut_candidates)

        hold_country.append(hold_series)

    country_df = pd.DataFrame(hold_country)

    country_df.to_csv(f'../data/LAC/counts/{country.lower()}_counts.csv') 


monthly_counts_flat('Colombia')
monthly_counts_flat('Ecuador')


### spare code for the poor

# main_cursor = db.lac.find(
#                 {   
#                     'event_type': {'$ne': '-999'},
#                     'exclude': {'$ne': True}
#                 }
#             )


# pull the docs - can just use the cursor once it gets bigger
# docs = [doc for doc in db.lac.find({'event_type': {'$ne':'-999'}, 'exclude':{'$ne': True}})]

# pull some additional info
# for _doc in tqdm(docs):
#     # get the text from the other db
#     art = db.articles.find_one({'url': _doc['url']})
#     _doc['gpe'] = []
#     # if they have translated
#     if 'title_translated' in art:
#         _doc['title'] = art['title_translated']
#         _doc['maintext'] = art['maintext_translated']
#     else: 
#         _doc['title'] = art['title']
#         _doc['maintext'] = art['maintext']

# def pull_gpe(doc):
#     if 'title_translated' in doc:
#         title = doc['title_translated']
#         maintext = doc['maintext_translated']
#     else:
#         title = doc['title']
#         maintext = doc['maintext']
#     gpe = []
#     gpe += [ee.text for ee in nlp(title).ents if ee.label_ == 'GPE']
#     gpe += [ee.text for ee in nlp(maintext).ents if ee.label_ == 'GPE']
#     return gpe

# from joblib import Parallel, delayed
# gpes = Parallel(n_jobs=12)(delayed(pull_gpe)(dd) for dd in tqdm(docs))

# some lines for inspecting documents
# rand_doc = docs[np.random.randint(low=0, high=len(docs))]
# rand_doc
# db.articles.find_one({'url': rand_doc['url']})['title']
# db.articles.find_one({'url': rand_doc['url']})['title_translated']
# db.articles.find_one({'url': rand_doc['url']})['maintext']
# db.articles.find_one({'url': rand_doc['url']})['maintext_translated']

# for _doc in ds :
#     art = db.articles.find_one({'url': _doc['url']})
#     print(art)

# for _doc in d_st :
#     print( db.articles.find_one({'url': _doc['url']}))
