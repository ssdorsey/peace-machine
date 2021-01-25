import os
from datetime import datetime
import os
from pathlib import Path
import pandas as pd
from dateutil.relativedelta import relativedelta

from simpletransformers.classification import ClassificationModel

from pymongo import MongoClient

from peacemachine.helpers import build_combined # TODO: convert to peacemachine.helpers

_ROOT = Path(os.path.abspath(os.path.dirname(__file__))).as_posix()

def get_data_path(path):
    return Path('/'.join(_ROOT.split('/')[:-1]), 'data', path).joinpath()

class EventClassifier:
    def __init__(self, uri, model_name, model_location, batch_size, n_gpu=1):
        self.uri = uri
        self.model_name = model_name
        self.model_location = model_location
        self.batch_size = batch_size
        self.n_gpu = n_gpu

    def get_db_info(self):
        """
        gets the info needed from the db
        """
        self.db = MongoClient(self.uri).ml4p # TODO: integrate db into uri
        self.model_info = self.db.models.find_one({'model_name': self.model_name})
        self.label_dict = {v:k for k,v in self.model_info.get('event_type_nums').items()}

    def load_model(self):
        """
        load the model
        TODO: convert to base transformers
        """
        self.model = ClassificationModel('roberta'
                            , f'{self.model_location}/{self.model_name}'
                            # , num_labels=18
                            , args={
                                'n_gpu': self.n_gpu
                                , 'eval_batch_size':self.batch_size})

    def generate_cursor(self, date):
        """
        creates the cursor for finding articles to process
        """
        colname = f'articles-{date.year}-{date.month}'
        self.cursor = self.db[colname].find(
                {
                    # needs model processing
                    self.model_name: {'$exists': False},
                    # in the proper language
                    'language': 'en',
                    # meant to be used
                    'include': True, 
                    # has a title
                    'title': {
                        '$exists': True,
                        '$ne': '',
                        '$ne': None
                    },
                    # 'source_domain': {'$in': }
                }
            )#.sort([('date_publish', -1)])
            

    def check_index(self):
        """
        checks to make sure that the model_name is indexed
        """
        indexes = [ll['key'].keys()[0] for ll in self.db.articles.list_indexes()]
        if self.model_name not in indexes:
            self.db.articles.create_index([(self.model_name, 1)], background=True)

    
    def zip_outputs(self, outputs):
        _mo = []

        for oo in outputs:
            _mo.append({self.label_dict[nn]: float(mo) for nn, mo in enumerate(oo)})

        return _mo


    def classify_articles(self):
        """
        function for classifying the articles in the queue
        """
        # do the predictions
        texts = [build_combined(doc) for doc in self.queue]
        preds, self.model_outputs = self.model.predict(texts)
        # modify outputs
        model_max = [float(max(mo)) for mo in self.model_outputs]
        self.event_types = [self.label_dict[ii] for ii in preds]
        # apply the cutoff
        for ii in range(len(model_max)):
            _et = self.event_types[ii]
            if model_max[ii] < self.model_info['event_type_cutoffs'][_et]:
                self.event_types[ii] = '-999'
        # zip up the model outputs
        self.model_outputs = self.zip_outputs(self.model_outputs)
        

    def insert_info(self):
        """
        inserts the docs into the db
        """
        for nn, _doc in enumerate(self.queue):
            colname = f"articles-{_doc['date_publish'].year}-{_doc['date_publish'].month}"
            self.db[colname].update_one(
                {
                    '_id': _doc['_id']
                },
                {
                    '$set':{
                        f'{self.model_name}': {
                            'event_type': self.event_types[nn],
                            'model_outputs': self.model_outputs[nn]
                        }
                    }
                }
            )

    def clear_queue(self):
        self.queue = []
        del self.event_types
        del self.model_outputs


    def run(self):
        self.get_db_info()
        self.check_index()
        self.load_model()

        dates = pd.date_range('2000-1-1', datetime.now()+relativedelta(months=1), freq='M')

        for date in dates:
            print(date)
            try:
                self.generate_cursor(date)
                # TODO: separate processes for queue and processing
                self.queue = []
                for doc in self.cursor:
                    self.queue.append(doc)

                    if len(self.queue) >= (self.batch_size * 10): 
                        self.classify_articles()
                        self.insert_info()
                        self.clear_queue()

                # one last time for any I missed
                self.classify_articles()
                self.insert_info()
                self.clear_queue()
            except: # TODO: detail exceptions
                pass

