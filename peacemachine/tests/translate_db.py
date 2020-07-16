import os
import time
import sys
import re
import pickle
import nltk
nltk.download('punkt')
from tqdm import tqdm
from pymongo import MongoClient
from urllib.parse import urlparse
import torch
from transformers import AutoTokenizer, AutoModelWithLMHead
import pandas as pd

if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p

# db = MongoClient('mongodb://ml4pAdmin:ml4peace@vpn.ssdorsey.com').ml4p

# -----------------------------
# classification model
# -----------------------------

# load the translation model
model_name = 'Helsinki-NLP/opus-mt-ROMANCE-en'
tokenizer = AutoTokenizer.from_pretrained(model_name)
# load the model 
lang_model = AutoModelWithLMHead.from_pretrained(model_name)
lang_model = lang_model.to('cuda')
    
# -----------------------------
# language model
# -----------------------------


# start with just Spanish 

_locals = ['extra.ec','eluniverso.com','elcomercio.com','eltelegrafo.com','lahora.com.ec','eldiario.ec','expreso.ec','metroecuador.com.ec','ultimasnoticias.ec','diarioque.ec','ppelverdadero.com.ec','elmercurio.com.ec','eltiempo.com.ec','laprensa.com.ec','lagaceta.com.ec','elnorte.ec','noticias.caracoltv.com','bluradio.com','noticias.canalrcn.com','lasillarota.com','lasillavacia.com','elespectador.com','eltiempo.com','portafolio.co','semana.com','canal1.com.co','elcolombiano.com','elheraldo.co','vanguardia.com','elnuevosiglo.com.co','eluniversal.com.co','elpais.com.co','lafm.com.co','citytv.com.co','diarioadn.co','pacifista.tv','razonpublica.com','verdadabierta.com','caracol.com.co','pulzo.com','cuestionpublica.com','lacoladerata.co','proclamadelcauca.com','universocentro.com','laorejaroja.com','lanuevaprensa.com.co','baudoap.com','sapienscol.com','rutasdelconflicto.com']
_internationals = ['apnews.com','reuters.com','bbc.com','nytimes.com','washingtonpost.com','aljazeera.com','theguardian','dw.com','france24.com','bloomberg.com','ft.com','wsj.com','csmonitor.com','latimes.com']

locals_regex = r'(extra\.ec|eluniverso\.com|elcomercio\.com|eltelegrafo\.com|lahora\.com\.ec|eldiario\.ec|expreso\.ec|metroecuador\.com\.ec|ultimasnoticias\.ec|diarioque\.ec|ppelverdadero\.com\.ec|elmercurio\.com\.ec|eltiempo\.com\.ec|laprensa\.com\.ec|lagaceta\.com\.ec|elnorte\.ec|caracoltv\.com|bluradio\.com|noticias\.canalrcn\.com|lasillarota\.com|lasillavacia\.com|elespectador\.com|eltiempo\.com|portafolio\.co|semana\.com|canal1\.com\.co|elcolombiano\.com|elheraldo\.co|vanguardia\.com|elnuevosiglo\.com\.co|eluniversal\.com\.co|elpais\.com\.co|lafm\.com\.co|citytv\.com\.co|diarioadn\.co|pacifista\.tv|razonpublica\.com|verdadabierta\.com|caracol\.com\.co|pulzo\.com|cuestionpublica\.com|lacoladerata\.co|proclamadelcauca\.com|universocentro\.com|laorejaroja\.com|lanuevaprensa\.com\.co|baudoap\.com|sapienscol\.com|rutasdelconflicto\.com)'


def batch_translate(list_strings, n=32):
    """
    batches and translates a list of strings
    :param list_strings: list of strings to translate
    :return: list of translated strings
    """
    # chunk the list into chunks size=n
    chunks = [list_strings[i:i + n] for i in range(0, len(list_strings), n)]
    # translate each chunk
    res = []
    for chunk in chunks:
        # convert to tensor batches
        batch = tokenizer.prepare_translation_batch(src_texts=chunk)
        # send tensors to cuda
        batch = batch.to('cuda')
        # translate
        translated_chunk = lang_model.generate(**batch)
        # decode
        translated_chunk = [tokenizer.decode(t, skip_special_tokens=True) for t in translated_chunk]
        # add back into master list
        res += translated_chunk
        del translated_chunk
        del batch
        torch.cuda.empty_cache()
    return res


def tci_locals(list_docs):
    ### pull what I want 

    to_translate = []

    for _doc in list_docs:
        to_translate.append([_doc['title'][:128], 'title', _doc['_id']])

        if _doc['maintext'] and len(_doc['maintext']) > 0:
            sent_tok = nltk.sent_tokenize(_doc['maintext'], language='spanish')
            # clip long and get rid of \n and ---
            sent_tok = [st[:256].replace('\n', '. ') for st in sent_tok]
            sent_tok = [re.sub(r'(-{3,})', ' ', st) for st in sent_tok]
            to_translate.append([sent_tok[0], 'mt0', _doc['_id']])
            if len(sent_tok) > 1:
                to_translate.append([sent_tok[1], 'mt1', _doc['_id']])
    
    #### translate
    start = time.time()
    translated = batch_translate([tt[0] for tt in to_translate])
    end = time.time()
    per_sec = len(translated) / (end-start)
    print('Translation iterations per second: ', per_sec)

    # merge back in 
    together = []
    for nn, tt in enumerate(to_translate):
        together.append(tt + [translated[nn]])

    title_df = pd.DataFrame([tt for tt in together if tt[1]=='title'], 
                            columns=['original', 'type', '_id', 'title'])
    title_df.drop(['type', 'original'], axis=1, inplace=True)

    mt0_df = pd.DataFrame([tt for tt in together if tt[1]=='mt0'], 
                            columns=['original', 'type', '_id', 'mt0'])
    mt0_df.drop(['type', 'original'], axis=1, inplace=True)

    mt1_df = pd.DataFrame([tt for tt in together if tt[1]=='mt1'], 
                            columns=['original', 'type', '_id', 'mt1'])
    mt1_df.drop(['type', 'original'], axis=1, inplace=True)

    df = title_df.merge(mt0_df, on='_id')
    df = df.merge(mt1_df, on='_id')

    # insert
    for ind in df.index:
        # insert everthing into article
        try:
            db.articles.update_one(
                {'_id': df['_id'].iloc[ind]}, 
                {'$set': {
                    'title_translated': df['title'].iloc[ind],
                    'maintext_translated': df.loc[ind, 'mt0'] +'. '+ df.loc[ind, 'mt1']
                }}
            )
        except:
            print('ERROR INSERTING')


if __name__ == "__main__":

    rc_re = re.compile(r'(China|Chinese|Chino|PRC|Russia|Rusia|Ruso|Rusa)', re.IGNORECASE)

    cursor = db.articles.find(
        {
            'source_domain': {'$in': _locals},
            'title':{'$ne': ''},
            'title_translated': {'$exists': False}, 
            # '$or': [
            #     {'title': {'$regex': rc_re}}, 
            #     {'maintext': {'$regex': rc_re}}
            # ]
        }
    ).batch_size(32)

    hold_locals = []

    for _doc in tqdm(cursor):
        hold_locals.append(_doc)
        if len(hold_locals) >= 32:
            print('DOING LOCALS')
            tci_locals(hold_locals)
            hold_locals = []

    # split into 8 pieces
    # rc_re = re.compile(r'(China|Chinese|Chino|PRC|Russia|Rusia|Ruso|Rusa)', re.IGNORECASE)

    cursor = db.articles.find(
        {
            'source_domain': {'$in': _locals},
            'title':{'$ne': ''},
            'title_translated': {'$exists': False}, 
            '$or': [
                {'title': {'$regex': rc_re}}, 
                {'maintext': {'$regex': rc_re}}
            ]
        }
    )

    # # get all the urls
    urls = [_doc['url'] for _doc in tqdm(cursor)]
    url_chunks = np.array_split(np.array(urls), 8)

    for nn, uc in enumerate(url_chunks):
        with open(f'DELETE_LAC_chunk{nn}.txt', 'w') as _file:
            for url in uc:
                _file.write(f'{url}\n')
