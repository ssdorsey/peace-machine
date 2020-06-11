from tqdm import tqdm
from urllib.parse import urlparse
from pymongo import MongoClient

rm = MongoClient("mongodb://ml4pAdmin:ml4peace@192.168.1.94/")

lc = MongoClient()

def check_url(doc, orig_col):
    """
    check to see if URL from old data is in new data
    """
    # pull url
    url = doc['url']
    # parse the url
    parsed = urlparse(url)
    # recon with netloc and path 
    nurl = parsed.netloc + parsed.path
    # filter out 'www.'
    if nurl.startswith('www.'):
        nurl = nurl[4:]
    # search 
    in_both_mod = bool(rm.ml4p.articles.find_one({'stripped_url': nurl}))
    # update
    update = orig_col.update_one(
        {
            '_id': doc['_id']
        },
        {
            '$set': {'in_new_db': in_both_mod}
        }
    )

# start by inserting a stripped url field into the rm database
# for doc in tqdm(rm.ml4p.articles.find({'stripped_url': {'$exists': False}})):
#     parsed = urlparse(doc['url'])
#     sturl = parsed.netloc + parsed.path
#     # strip www.
#     sturl = sturl.replace('www.', '')
#     res = rm.ml4p.articles.update_one(
#         {
#             '_id': doc['_id']
#         },
#         {
#             '$set': {'stripped_url': sturl}
#         }
#     )


# # check missing from articles
# for _doc in tqdm(lc.ml4p.articles.find()):
#     check_url(_doc, lc.ml4p.articles)

# # check missing from events
# for _doc in tqdm(lc.ml4p.events.find()):
#     check_url(_doc, lc.ml4p.events)

# # check missing from sites
# for _doc in tqdm(lc.ml4p.sites.find()):
#     check_url(_doc, lc.ml4p.sites)

# # check missing from serbia
# for _doc in tqdm(lc.ml4p.serbia.find()):
#     check_url(_doc, lc.ml4p.serbia)


# summarize missing 
for col in ['sites', 'articles', 'events', 'serbia']:
    cursor = lc.ml4p[col].find({'in_new_db': False})
    for _doc in tqdm(cursor):
        with open(f'{col}_missing.txt', 'a', encoding='utf8') as _file:
            _file.write(_doc['url'])
            _file.write('\n')
