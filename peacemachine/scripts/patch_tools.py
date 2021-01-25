import os
import getpass
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
import json
from tqdm import tqdm
from p_tqdm import p_umap
from pymongo import MongoClient
from pymongo.errors import CursorNotFound
from pymongo.errors import DuplicateKeyError

from peacemachine.helpers import regex_from_list
from peacemachine.helpers import download_url


if getpass.getuser() in ['Batan', 'spenc']: #TODO convert this over to a command-line read
    uri = 'mongodb://ml4pAdmin:ml4peace@192.168.176.240'
else:
    uri = 'mongodb://ml4pAdmin:ml4peace@vpn.ssdorsey.com'

db = MongoClient(uri).ml4p

def remove_blacklist(col_name):
    # print('STARTING BLACKLIST')
    # db = MongoClient(uri).ml4p
    sources = db.sources.find(
        {
            'blacklist_url_patterns': {'$ne': []}
        }
    )
    for source in sources:
        while True:
            try:
                black = source.get('blacklist_url_patterns')
                black_re = regex_from_list(black)

                db[col_name].delete_many(
                    {
                        'source_domain': source.get('source_domain'),
                        'url': {'$regex': black_re}
                    }
                )
                
            except CursorNotFound:
                print('Cursor error, restarting')
                continue

            break


def add_whitelist(colname):
    """
    filters whitelist sites
    """
    # print('STARTING WHITELIST')

    # db = MongoClient(uri).ml4p

    # sources without whitelists first
    sources = db.sources.find(
        {
            'include': True,
            '$or': [
                {'whitelist_url_patterns': []},
                {'whitelist_url_patterns': {'$exists': False}}
            ]
        }
    )
    for source in sources:
        # deal with the sources that don't have a whitelist
        if not(source.get('whitelist_url_patterns')):
            db[colname].update_many(
                {
                    'source_domain': source.get('source_domain')
                },
                {
                    '$set': {
                        'include': True
                    }
                }
            )

    # sources with whitelists next
    sources = db.sources.find(
        {
            'include': True,
            '$or': [
                {'whitelist_url_patterns': {'$ne': []}}
            ]
        }
    )
    for source in sources:
        source_regex = regex_from_list(source.get('whitelist_url_patterns'), compile=False)
        db[colname].update_many(
            {
                'source_domain': source.get('source_domain'),
                'url': {'$regex': source_regex}
            },
            {
                '$set': {
                    'include': True
                }
            }
        )
    

def add_otherlist(colname):
    """
    doesn't delete but doesn't include sites with other_url_patterns
    """
    # print('FILTERING OTHER_URL_PATTERNS')
    # db = MongoClient(uri).ml4p

    sources = db.sources.find(
        {
            'other_url_patterns': {
                '$exists': True,
                '$ne': []
            }
        }
    )

    for source in sources:
        source_regex = regex_from_list(source.get('other_url_patterns'), compile=False)
        db[colname].update_many(
            {
                'source_domain': source.get('source_domain'),
                'url': {'$regex': source_regex}
            },
            {
                '$set': {
                    'include': False
                }
            }
        )


def create_year_month(colname):
    # print('CREATING YEAR AND MONTH FIELDS')
    # db = MongoClient(uri).ml4p

    cursor = db[colname].find(
        {
            'date_publish': {
                '$exists': True,
                '$type': 'date'
            },
            'month': {'$exists': False}
        }
    )
    for doc in cursor:
        db[colname].update_one(
            {'_id': doc['_id']},
            {
                '$set':{
                    'year': doc['date_publish'].year,
                    'month': doc['date_publish'].month
                }
            }
        )


def dedup_collection(colname):

    # print('STARTING DEDUP')
    db = MongoClient(uri).ml4p

    # loc = [doc['source_domain'] for doc in db['sources'].find(
    #     {
    #         'primary_location': {'$in': ['PRY', 'ECU', 'COL']},
    #         'include': True
    #     }
    # )]

    # cursor = db[colname].find({'source_domain': {'$in': loc}}, batch_size=1)
    cursor = db[colname].find({}, batch_size=1)

    mod_count = 0

    for _doc in cursor:
        try:
            # get the date filters
            start = _doc['date_publish'].replace(hour=0, minute=0, second=0)
            end = start + relativedelta(days=1)

            res = db[colname].delete_many(
                {
                    '_id': {'$ne': _doc['_id']},
                    'date_publish': {'$gte': start, '$lt': end},
                    'source_domain': _doc['source_domain'],
                    'title': _doc['title']
                }
            )

            if res.deleted_count != 0:
                mod_count += res.deleted_count
        except:
            pass
    
    print(f'{colname} DELETED: {mod_count}')


def split_date(date):
    year = date.year
    month = date.month
    # db = MongoClient(uri).ml4p

    cur = db.articles.find(
        {
            'year': year,
            'month': month,
            # 'in_split': {'$ne': True}
        }
    )

    docs = [doc for doc in cur]
    for doc in docs:
        doc.pop('_id', None)
        doc.pop('localpath', None)

    colname = f'articles-{year}-{month}'

    if colname not in [ll for ll in db.list_collection_names()]:
        db.create_collection(colname)
        db[colname].create_index('url', unique=True)
        db[colname].create_index('source_domain')
        db[colname].create_index('date_publish')
        db[colname].create_index('title')
        db[colname].create_index('civic1.event_type')
        db[colname].create_index('RAI.event_type')

    for doc in docs:
        try:
            db[colname].insert_one(doc)

        except:
            pass
            # print('INSERT ERROR')


def process_ccnews_domain(path):
    """
    process an individual ccnews folder dump
    """
    
    _files = [ff for ff in os.listdir(path) if ff.endswith('.json')]
    count = 0
    for ff in _files:
        with open(path+ff, 'r', encoding='utf-8') as _file:
            _data = json.load(_file)

        try:
            _data['date_publish'] = dateparser.parse(_data['date_publish'])
            colname = f"articles-{_data['date_publish'].year}-{_data['date_publish'].month}"
        except:
            colname = 'nodate'
        
        try:
            db[colname].insert_one(_data)
            count += 1
        except DuplicateKeyError:
            pass

    print(f'INSERTED STORIES FOR {path}: {count}')


def import_ccnews(path):
    """
    process all of the folders in a ccnews dump
    """
    doms = os.listdir(path)
    doms = [dd for dd in doms if dd in db.sources.distinct('source_domain')]
    dom_paths = [path+dd+'/' for dd in doms]

    p_umap(process_ccnews_domain, dom_paths)        


def fix_language(colname):
    db[colname].update_many(
        {
            'title_original': {'$exists': True},
            'language': {'$ne': 'en'}
        },
        {
            '$set': {
                'language': 'en'
            }
        }
    )

def redo_doc_date(doc):
    """
    rescrapes the date for a doc
    """
    url = doc.get('url')
    old_date = doc.get('date_publish')
    old_col = f"articles-{old_date.year}-{old_date.month}"

    new_doc = download_url(uri, url, insert=False)
    new_date = new_doc.get('date_publish')
    new_col = f"articles-{new_date.year}-{new_date.month}"

    if new_col != old_col:
        # fix the date 
        doc['date_publish'] = new_doc.get('date_publish')
        # insert the doc into the correct collection
        db[new_col].insert_one(doc)
        # delete the old one
        db[old_col].delete_one({'_id': doc['_id']})


def rescrape_date(domain, colname):
    """
    rescrapes the dates for every article in the domain/collection combo
    """
    docs = [doc for doc in db[colname].find({'source_domain': domain})]
    for doc in docs:
        try:
            redo_doc_date(doc)
        except:
            print(f'ERROR on {doc["url"]}')


def rescrape_source(colname, domain):
    """
    Rescrapes everything from a given source
        (usually because it needed a custom parser)
    """
    docs = [doc for doc in db[colname].find({'source_domain', domain})]
    for doc in docs:
        download_url(uri, doc['url'], overwrite=True)


def rescrape_gazetatemanet(colname):
    """
    Rescrape the gazetatema stories that are missing their maintext
    """
    print('starting '+colname)
    cur = db[colname].find(
        {
            'source_domain': 'gazetatema.net',
            '$or': [
                    {'maintext': '.'},
                    {'maintext': {'$regex': '^We use cookies to improve your experience.'}},
                    {'maintext': {'$type': 'null'}}
                ]
        }
    )
    for doc in cur:
        download_url(uri, doc['url'], overwrite=True)

def remove_bad_translations(colname, language):
    """
    Removes translations (and model classifications) for a given collection and language
    """
    cur = db[colname].find({'language_original': language})

    for doc in cur:
        db[colname].update_one(
            {
                '_id': doc['_id']
            },
            {
                '$set': {
                    'language': 'language_original',
                    'title': 'title_original',
                    'maintext': 'maintext_original'
                }, 
                '$unset': { 
                    'language_original': 1,
                    'title_original': 1,
                    'maintext_original': 1,
                }
            }
        )


if __name__ == "__main__":
    # dates = pd.date_range('2000-1-1', '2020-12-1', freq='M')
    # p_umap(split_date, dates[190:], num_cpus=8)

    colnames = [ll for ll in db.list_collection_names() if ll.startswith('articles-')]
    colnames = [ll for ll in colnames if ll != 'articles-nodate']
    colnames = [ll for ll in colnames if int(ll.split('-')[1]) >= 2000]
    # sort by most recent
    colnames = sorted(colnames, key = lambda x: (int(x.split('-')[1]), int(x.split('-')[2])), reverse=True)
    # colnames = [ll for ll in colnames if ll.startswith('articles-2020')]
    print('blacklist')
    p_umap(remove_blacklist, colnames, num_cpus=8)
    print('whitelist')
    p_umap(add_whitelist, colnames, num_cpus=8)
    print('otherlist')
    p_umap(add_otherlist, colnames, num_cpus=8)

    # for doc in tqdm(db['articles-nodate'].find({'source_domain': 'assabah.ma'})):
    #     download_url(uri=uri, url=doc['url'])


    # tt = db['articles-nodate'].find_one({'source_domain': 'assabah.ma'})
    # url = 'https://assabah.ma/515817.html'
    # tt_d = download_url(uri=uri, url=url, insert=False)

    print('dedup')
    p_umap(dedup_collection, colnames, num_cpus=8)

    # print('remove Georgian')
    # p_umap(remove_bad_translations, colnames, ['ka']*len(colnames))

    # colnames = [ll for ll in colnames if ll not in ['articles-2020-7', 'articles-2020-8']]
    # p_umap(rescrape_gazetatemanet, colnames, num_cpus=4)
    
    # print('redoing dates')
    # doms = ['kbc.co.ke', 'theeastafrican.co.ke', 'businessdailyafrica.com']
    # rep_doms = doms * len(colnames)
    # rep_colnames = sorted(colnames * len(doms))

    # p_umap(rescrape_date, rep_doms, rep_colnames, num_cpus=12)









# for col in tqdm(colnames):
#     fix_language(col)

# for col in tqdm(colnames):
#     try:
#         urls = [{'url': doc.get('url')} for doc in db[col].find()]
#         db.urls.insert_many(urls, ordered=False)
#     except:
#         pass



# import_ccnews('D:/cc_articles~/cc_download_articles/')

# p_umap(create_year_month, colnames, num_cpus=10)
# db = MongoClient(uri).ml4p
# cur = db.articles.find(
#     {
#         'language': 'en',
#         'title_translated': {'$exists': True}
#     }
# )

# for _doc in tqdm(cur):
#     # set new
#     db.articles.update_one(
#         {
#             '_id': _doc['_id']
#         },
#         {
#             '$set': {
#                 'title_original': _doc.get('title'),
#                 'maintext_original': _doc.get('maintext'),
#                 'title': _doc.get('title_translated'),
#                 'maintext': _doc.get('maintext_translated'),
#             }
#         }
#     )
#     # take away misclassified
#     db.articles.update_one(
#         {
#             '_id': _doc['_id']
#         },
#         {
#             '$unset': {
#                 'civic1': 1,
#                 'RAI': 1,
#                 'title_translated': 1,
#                 'maintext_translated': 1,
#             }
#         },
#     )


# db = MongoClient(uri).ml4p
# sites = []
# counts = []
# for source in db.sources.find():
#     sd = source.get('source_domain')
#     sites.append(sd)
#     counts.append(db.articles.count_documents({'source_domain': sd}))

# df = pd.DataFrame({'site': sites, 'count': counts})

# import plotly.express as px
# fig = px.bar(df, x='site', y='count')
# fig.show()


# db.sources.update_one(
#     {
#         'source_domain': 'elheraldo.co'
#     },
#     {
#         '$set': {
#             'blacklist_url_patterns': db.sources.find_one({'source_domain': 'elheraldo.co'}).get('blacklist_url_patterns') + ['/horoscopo/']
#         }
#     }
# )



# ##### process to find problematic url snippets



# def check_sections(sd):
#     """
#     :param sd: source_domain to check section counts
#     """
#     urls = [doc['url'] for doc in db.articles.find({'source_domain': sd})]

#     m_sections = []
#     for url in urls:
#         url = url[url.index(sd)+len(sd): ]
#         sections = [sec for sec in url.split('/')[:-1] if sec]
#         m_sections += sections

#     sec = pd.Series(m_sections)
#     counts = pd.DataFrame(sec.value_counts())
#     counts = counts.reset_index()
#     counts = counts.rename(columns={'index':'site', 0: 'count'})

#     return counts

# eles = check_sections('elespectador.com').iloc[:50]
# fig = px.bar(eles, x='site', y='count')
# fig.show()

# Fix stuff where the translation went ary

# doms = [
#     'elcolombiano.com',
#     'elespectador.com',
#     'elheraldo.co',
#     'eltiempo.com',
#     'portafolio.co'
# ]


# russia = pd.read_excel(r"D:\Dropbox\peace-machine\peacemachine\data\actors\Acronyms_Russia.xlsx")
# # russia_re = '(' + '|'.join(russia['CompanyName']) + ')'

# china = pd.read_excel(r"D:\Dropbox\peace-machine\peacemachine\data\actors\Acronyms_China.xlsx")
# china['CompanyName'] = china['CompanyName'].str.strip()
# # china_re = '(' + '|'.join(china['CompanyName']) + ')'

# rai_re = '(' + '|'.join(pd.concat([russia['CompanyName'], china['CompanyName']])) + ')'

# cur = db['articles-2020-2'].find(
#     {
#         'source_domain': {'$in': doms},
#         'RAI.event_type': 'tech_transfer_investment',
#         'include': True,
#         '$or': [
#             {'title': {'$regex': rai_re}},
#             {'maintext': {'$regex': rai_re}}
#         ]
#     }
# )

# docs = [doc for doc in cur]

# df = pd.DataFrame(docs)

# df.to_csv('peacemachine/tests/DELETE_tech_transfer.csv', index=False)

# db['articles-2017-8'].find_one({'url': 'http://www.paraguay.com/nacionales/intenso-simulacro-de-toma-de-rehenes-en-aeropuerto-silvio-pettirossi-166542'})

# db.languages.insert_one(
#     {
#         'iso_name': 'Ukrainian',
#         'iso_code': 'uk',
#         'model_type': 'huggingface',
#         'huggingface_name': 'Helsinki-NLP/opus-mt-uk-en',
#         'model_location': ''
#     }
# )

# doc = db['articles-2019-4'].find_one(
#     {
#         'url': 'https://www.abc.com.py/internacionales/argentina-congela-precios-y-tarifas-ante-aceleracion-inflacionaria-1806181.html'
#     }
# )


# count = 0 
# for col in colnames:
#     count += db[col].count()
# count

