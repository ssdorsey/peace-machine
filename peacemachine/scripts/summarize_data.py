import random
from tqdm import tqdm
import pymongo

cl = pymongo.MongoClient()
db = cl.ml4p

with open('../../data/domains/domains_Nigeria.txt', 'r') as _file:
    n_doms = [dd.strip() for dd in _file.readlines()]

def domain_summary(domains):

    hold_results = {}

    for dd in tqdm(domains):

        count_articles = db.articles.count_documents(
            {'url': {'$regex': dd}}
        ) 
        count_events = db.events.count_documents(
            {'domain': dd}
        )
        sample_articles = db.articles.find(
            {'url': {'$regex': dd}}
        ).limit(1).skip(random.randint(0, 1000))
        sample_events = db.events.find(
            {'domain': dd}
        ).limit(1).skip(random.randint(0, 1000))

        hold_results[dd] = {
            'count_articles': count_articles, 
            'count_events': count_events, 
            'sample_articles': [doc for doc in sample_articles],
            'sample_events': [doc for doc in sample_events]
        }
    
    return hold_results

n_sum = domain_summary(n_doms)

n_sum[n_doms[1]]

for kk, vv in n_sum.items():
    print(kk)
    print(vv['count_articles'] - vv['count_events'])

