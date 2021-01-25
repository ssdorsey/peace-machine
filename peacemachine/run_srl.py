import re
import nltk
from allennlp.predictors import Predictor
from pymongo import MongoClient
from pymongo.errors import CursorNotFound
from tqdm import tqdm

db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p

batch_size = 256

predictor = Predictor.from_path(
    "https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.11.19.tar.gz", 
    cuda_device=0
)
# res = predictor.predict_batch_json(
#   [{'sentence':"This is a test."}]*512
# )

def cut_dateline(text, thresh=30):
    """
    removes the dateline from the beginning of a news story
    :param text: string, generally the body of a news story that may have a 
                    dateline
    :param thresh: how far into the text to look for the dateline indicators
    :return: string with dateline cut out
    """
    if ' — ' in text[:30]:
        return text[text.index(' — ')+3:]
    elif '--' in text[:30]:
        return text[text.index('--')+2:]
    elif ' - ' in text[:30]:
        return text[text.index(' - ')+3:]
    # get rid of the CNN dateline
    elif '(CNN)' in text[:30]:
        return text[text.index('(CNN)')+5:]
    elif ': ' in text[:20]:
        return text[text.index(': ')+2:]
    elif '\n' in text[:20]:
        return text[text.index('\n')+1:]
    # if no dateline is found, return the same string
    return text


def process_batch(colname, list_docs):
    titles = [{'sentence': doc['title']} for doc in list_docs]
    texts = []
    for doc in list_docs:
        try:
            texts.append({'sentence': nltk.sent_tokenize(cut_dateline(doc['maintext']))[0]})
        except:
            texts.append({'sentence': ''})

    titles_srl = predictor.predict_batch_json(titles)
    texts_srl = predictor.predict_batch_json(texts)

    for nn, doc in enumerate(list_docs):
        db[colname].update_one(
            {'_id': doc['_id']},
            {
                '$set': {
                    'title_srl': titles_srl[nn],
                    'maintext_srl': texts_srl[nn]
                }
            }
        )
        

def generate_cursor(colname):
    """
    Generates a new pymongo cursor for the given collection
    """
    cursor = db[colname].find(
        {
            'language': 'en', 
            'title_srl': {'$exists': False},
            '$and': [
                {'title': {'$exists': True}},
                {'title': {'$ne': ''}},
                {'title': {'$not': {'$type': 'null'}}}
            ]
        },
        no_cursor_timeout=True
    )

    return cursor

def collection_srl(colname):
    count =  db[colname].count_documents(
        {
            'language': 'en', 
            'title_srl': {'$exists': False},
            '$and': [
                {'title': {'$exists': True}},
                {'title': {'$ne': ''}},
                {'title': {'$not': {'$type': 'null'}}}
            ]
        }
    )

    cur = generate_cursor(colname)

    queue = []
    for doc in tqdm(cur, total=count):
        queue.append(doc)

        if len(queue) >= batch_size:
            try:
                process_batch(colname, queue)
            except Exception as e:
                print(e)
            queue = []
            # cur = generate_cursor(colname)


    if len(queue) > 0:
        print('last batch')
        process_batch(colname, queue)

    print(f'{colname} complete')

colnames = [ll for ll in db.list_collection_names() if ll.startswith('articles-')]
colnames = [ll for ll in colnames if ll != 'articles-nodate']
colnames = [ll for ll in colnames if int(ll.split('-')[1]) >= 2000]
# sort by most recent
colnames = sorted(colnames, key = lambda x: (int(x.split('-')[1]), int(x.split('-')[2])), reverse=True)


for col in colnames:
    print(col)
    collection_srl(col)

# colname = 'articles-2020-10'
# db[colname].count_documents(
#         {
#             'language': 'en', 
#             'title_srl': {'$exists': False},
#             '$and': [
#                 {'title': {'$exists': True}},
#                 {'title': {'$ne': ''}},
#                 {'title': {'$not': {'$type': 'null'}}}
#             ]
#         }
#     )

# collection_srl(colname)