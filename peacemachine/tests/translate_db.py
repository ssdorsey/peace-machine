import os
import time
import sys
import re
import pickle
import nltk
# nltk.download('punkt')
from tqdm import tqdm
from pymongo import MongoClient
from urllib.parse import urlparse
import torch
from transformers import AutoTokenizer, AutoModelWithLMHead
from simpletransformers.classification import ClassificationModel

if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@devlab-server').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p

def cut_dateline(_string, thresh=30):
    """
    removes the dateline from the beginning of a news story
    :param text: string, generally the body of a news story that may have a 
                    dateline
    :param thresh: how far into the text to look for the dateline indicators
    :return: string with dateline cut out
    """
    try:
        if ' —' in _string[:thresh]:
            return _string[_string.index(' —')+2:]
        elif '--' in _string[:thresh]:
            return _string[_string.index('--')+2:]
        elif ' -' in _string[:thresh]:
            return _string[_string.index(' -')+2:]
        elif ': ' in _string[:thresh-10]:
            return _string[_string.index(': ')+2:]
        elif bool(re.search(r'(\(.*?\)\s)', _string[:thresh])):
            return re.sub(r'(\(.*?\))', '', _string)
        # if no dateline is found, return the same string
        return _string
    except AttributeError:
        return ''


# -----------------------------
# classification model
# -----------------------------
label_dict = pickle.load( open( "../data/LAC/label_dict.p", "rb" ) )
label_dict = {v:k for k,v in label_dict.items()}

# TODO: convert to CLASS

# def load_models(reload_models=False):
#     """
#     load the default translation and classification models
#     """
#     if reload_models:
#         del class_model
#         del lang_model
#         torch.cuda.empty_cache()
# load the classification model
class_model = ClassificationModel('roberta'
                            , '../data/LAC/StackedModel_no999'
                            , num_labels=25
                            , args={
                                'n_gpu':1
                                ,'eval_batch_size':768})
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


def batch_translate(list_strings, n=16):
    """
    batches and translates a list of strings
    :param list_strings: list of strings to translate
    :return: list of translated strings
    """
    # chunk the list into chunks size=n
    chunks = [list_strings[i:i + n] for i in range(0, len(list_strings), n)]
    # translate each chunk
    translated = []
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
        translated += translated_chunk
        del translated_chunk
        del batch
        torch.cuda.empty_cache()
    return translated


def tci_locals(list_docs):
    #### translate
    # pull the pieces of the doc
    titles = [ld['title'][:200] for ld in list_docs]
    first_sentences = []
    for ld in list_docs:
        if ld['maintext']:
            try:
                cut = cut_dateline(ld['maintext'])
                first_sentences.append(nltk.sent_tokenize(cut)[0][:400])
            except:
                first_sentences.append('nan')
        else:
            first_sentences.append('nan') # TODO: figured out a better way to deal with empty strings
    
    translated_titles = batch_translate(titles)
    translated_first_sentences = batch_translate(first_sentences)

    #### classify
    translated_combined = [translated_titles[ii] + ' ' +
                            translated_first_sentences[ii] for 
                            ii in range(len(translated_titles))]
    preds, model_outputs = class_model.predict(translated_combined)
    preds_cut = preds
    # modify outputs
    model_max = [float(max(mo)) for mo in model_outputs]
    # threshold for 999
    for ii in range(len(model_max)):
        if model_max[ii] < 7: # TODO: CHECK THIS CUTOFF
            preds_cut[ii] = 0
    pred_types = [label_dict[ii] for ii in preds_cut]
    # insert
    for nn, ld in enumerate(list_docs):
        # insert everthing into article
        ld['title_translated'] = translated_titles[nn]
        ld['maintext_translated'] = translated_first_sentences[nn]
        db.articles.update_one(
            {'_id': ld['_id']}, 
            {'$set': {
                'title_translated':ld['title_translated'],
                'maintext_translated': ld['maintext_translated']
            }}
        )
        # now insert into the new lac category
        # drop the categories I don't want
        ld = {kk:vv for kk, vv in ld.items() if kk in {'url', 'date_publish', 'bad_location'}}
        # insert only url, date_publish, bad_location, event_type info to lac collection
        ld['event_type'] = pred_types[nn]
        ld['model_outputs'] = [float(num) for num in model_outputs[nn]]
        try:
            db.lac.replace_one({'url':ld['url']}, ld, upsert=True)
        except:
            print('ERROR ON: ', ld['url'])
            pass

def tci_internationals(list_docs):
    #### translate
    # pull the pieces of the doc
    titles = [ld['title'][:200] for ld in list_docs]
    first_sentences = []
    for ld in list_docs:
        if ld['maintext']:
            cut = cut_dateline(ld['maintext'])
            first_sentences.append(nltk.sent_tokenize(cut)[0][:400])
        else:
            first_sentences.append('nan') # TODO: figured out a better way to deal with empty strings

    #### classify
    combined = [titles[ii] + ' ' + first_sentences[ii] for ii in range(len(titles))]
    preds, model_outputs = class_model.predict(combined)
    preds_cut = preds
    # modify outputs
    model_max = [float(max(mo)) for mo in model_outputs]
    # threshold for 999
    for ii in range(len(model_max)):
        if model_max[ii] < 7: # TODO: CHECK THIS CUTOFF
            preds_cut[ii] = 0
    pred_types = [label_dict[ii] for ii in preds_cut]
    # insert
    for nn, ld in enumerate(list_docs):
        # now insert into the new lac category
        # drop the categories I don't want
        ld = {kk:vv for kk, vv in ld.items() if kk in {'url', 'date_publish', 'bad_location'}}
        # insert only url, date_publish, bad_location, event_type info to lac collection
        ld['event_type'] = pred_types[nn]
        ld['model_outputs'] = [float(num) for num in model_outputs[nn]]
        try:
            db.lac.replace_one({'url':ld['url']}, ld, upsert=True)
        except:
            print('ERROR ON: ', ld['url'])
            pass


if __name__ == "__main__":
    # load models
    # load_models()

    cursor = db.articles.find()

    rc_re = re.compile(r'(China|Chinese|Chino|PRC|Russia|Rusia|Ruso|Rusa)', re.IGNORECASE)
    ec_re = re.compile(r'(Ecuador|Colombia)', re.IGNORECASE)

    hold_locals = []
    hold_internationals = []

    for _doc in tqdm(cursor):
        try:
            # pull the domain
            domain = pull_domain(_doc['url'])
            # deal with missing text
            try:
                all_text = _doc['title'] + ' ' + _doc['maintext']
            except:
                all_text = _doc['title']

            # attach qualifying document to a holding list as I loop through
            if domain in _locals:
                if (bool(rc_re.search(all_text))): # mentions China or Russia
                    # and not bool(db.lac.find_one({'url':_doc['url']}))): # not already encoded
                    hold_locals.append(_doc)
            
            if domain in _internationals:
                if (bool(rc_re.search(all_text)) # mentions China or Russia
                    and bool(ec_re.search(all_text))): # mentions Ecuador or Colombia
                    # and not bool(db.lac.find_one({'url':_doc['url']}))): # not already encoded
                    hold_internationals.append(_doc)
        except:
            print('ERROR!')
            pass

        # if either document bank hits 768, process the docs before collecting more
        if len(hold_locals) >= 768:
            # print('GOT LOCALS BATCH')
            # break
            print('DOING LOCALS')
            tci_locals(hold_locals)
            hold_locals = []

        if len(hold_internationals) >= 768:
            # print('GOT INTERNATIONALS BATCH')
            # break
            print('DOING INTERNATIONALS')
            tci_internationals(hold_internationals)
            hold_internationals = []

    # get all the leftovers
    if len(hold_locals) > 0:
        tci_locals(hold_locals)

    if len(hold_internationals) > 0:
        tci_internationals(hold_internationals)
