import os
import json
from datetime import datetime
from dateutil.parser import parse
from tqdm import tqdm
from pymongo import MongoClient

db = MongoClient('mongodb://ml4pAdmin:ml4peace@devlab-server').ml4p

file_names = []
for folder in os.listdir('D:/Dropbox/office-ccnews'):
    file_names.extend([folder+'/'+ff for ff in os.listdir('D:/Dropbox/office-ccnews/'+folder)])

json_bank = []
for fn in tqdm(file_names):
    with open('D:/Dropbox/office-ccnews/'+fn, 'r', encoding='utf-8') as _file:
        _json = json.load(_file)
    if not isinstance(_json['date_publish'], datetime):
        try:
            _json['date_publish'] = parse(_json['date_publish'])
            json_bank.append(_json)
        except:
            print("date didn't work...")

    if len(json_bank) > 10000:
        try:
            db.articles.insert_many(
                json_bank, 
                ordered=False
            )
        except:
            print('ERROR ON BULK INSERT')
        json_bank = []
    
