import re
import time
from tqdm import tqdm
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import urlparse
import torch
from transformers import MarianMTModel, MarianTokenizer
from pymongo import MongoClient

# import peacemachine stuff
# from peacemachine.helpers import UrlFilter

# TODO: switch to "title" + "maintext" / "title_original" + "maintext_original"

def translate_pipe(uri, language, batch_size):
    """
    :param uri: The MongoDB uri for connecting to the main DB
    :param language: the iso2 code for the language to translate or "all" 
    """
    db = MongoClient(uri).ml4p

    if language == 'all':
        all_languages = db['languages'].distinct('language')
        for lang in all_languages:
            trans = Translator(uri, lang, batch_size)
            trans.run()

    elif isinstance(language, list):
        for lang in language:
            trans = Translator(uri, lang, batch_size)
            trans.run()

    else:
        trans = Translator(uri, language, batch_size)
        trans.run()


class Translator:

    def __init__(self, mongo_uri, language, batch_size):
        """
        :param mongo_uri: the uri for the db
        :param language: the iso2 language to translate for translation
        """
        self.mongo_uri = mongo_uri
        self.language = language
        self.batch_size = batch_size

        self.db = MongoClient(mongo_uri).ml4p
        self.lang_info = self.db['languages'].find_one({'iso_code': language})
        self.model_type = self.lang_info['model_type']
        # self.model_location = self.lang_info['model_location']
        self.huggingface_name = self.lang_info['huggingface_name'] # ex 'Helsinki-NLP/opus-mt-ROMANCE-en'

        # get a filter instance going
        # self.filter = UrlFilter()

    def prep_batch(self, chunk, max_length):
        return self.tokenizer.prepare_seq2seq_batch(src_texts=chunk, max_length=max_length)

    def batch_translate(self, list_strings, max_length=100, num_beams=4):
        """
        batches and translates a list of strings
        :param list_strings: list of strings to translate
        :return: list of translated strings
        """
        # chunk the list into chunks size=n
        chunks = [list_strings[i:i + self.batch_size] for i in range(0, len(list_strings), self.batch_size)]
        chunks = [self.prep_batch(ch, max_length) for ch in chunks]
        # translate each chunk
        res = []
        for chunk in chunks:
            # send tensors to cuda
            batch = chunk.to('cuda')
            # translate
            translated_chunk = self.lang_model.generate(
                **batch,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True
            )
            # decode
            translated = self.tokenizer.batch_decode(translated_chunk, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            # add back into master list
            res += translated
        return res

    def fix_maintext(self, mt):
        if not mt:
            return '.'
        try:
            mt = re.sub(r'(\n)', '. ', mt)
            mt = re.sub(r'(-{3,})', ' ', mt)
        except AttributeError:
            return '.'
        except TypeError:
            return '.'
        return mt


    def tci_locals(self):
        ### pull what I want 
        _ids = [_doc['_id'] for _doc in self.list_docs]

        raw_titles = [_doc['title'] for _doc in self.list_docs]

        raw_maintext = [_doc['maintext'] for _doc in self.list_docs]
        raw_maintext = [self.fix_maintext(rm) for rm in raw_maintext]

        #### translate
        start = time.time()
        translated_titles = self.batch_translate(raw_titles)
        translated_maintext = self.batch_translate(raw_maintext)
        end = time.time()
        # per_sec = len(translated_titles)*2 / (end-start)
        # print('Translation iterations per second: ', per_sec)
        print(f'Articles translated in {self.colname}: ' + str(len(translated_titles)))

        # insert
        for nn, _id in enumerate(_ids):
            # insert everthing into article
            # _year = self.list_docs[nn]['date_publish'].year
            # _month = self.list_docs[nn]['date_publish'].month
            # colname = f'articles-{_year}-{_month}'
            try:
                self.db[self.colname].update_one(
                    {'_id': _id}, 
                    {'$set': {
                        # keep the original
                        'title_original': self.list_docs[nn].get('title'),
                        'maintext_original': self.list_docs[nn].get('maintext'),
                        'language_original': self.list_docs[nn].get('language'),
                        # insert the new
                        'title': translated_titles[nn],
                        'maintext': translated_maintext[nn],
                        'language': 'en'
                    }}
                )
            except:
                print('ERROR INSERTING')

    def run(self):
        """
        main function to run the translator
        """
        if self.model_type == 'huggingface':
            # load the translation model
            self.tokenizer = MarianTokenizer.from_pretrained(self.huggingface_name)
            # load the model 
            self.lang_model = MarianMTModel.from_pretrained(self.huggingface_name)
            self.lang_model = self.lang_model.to('cuda')

            dates = pd.date_range('2000-1-1', datetime.now()+relativedelta(months=1), freq='M')

            for date in dates:
                self.colname = f'articles-{date.year}-{date.month}'

                cursor = self.db[self.colname].find(
                    {
                        # 'source_domain': {'$in': loc},
                        'language': self.language,
                        'include': True,
                        'title':{'$ne': ''},
                        'title':{'$not': {'$type': 'null'}},
                        'title_original': {'$exists': False}, 
                    }
                ).batch_size(128)

                self.list_docs = []

                for _doc in tqdm(cursor):
                    self.list_docs.append(_doc)
                    if len(self.list_docs) >= 128:
                        print('Translating')
                        try:
                            self.tci_locals()
                        except ValueError:
                            print('ValueError')
                        except AttributeError:
                            print('AttributeError')
                        self.list_docs = []

                # handle whatever is left over
                self.tci_locals()
                self.list_docs = []


        elif self.model_type == 'opennmt':
            # TODO: fill out the opennmt process
            pass
