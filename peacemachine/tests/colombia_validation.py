import os
import pandas as pd
import numpy as np
from pymongo import MongoClient
import nltk

from tqdm import tqdm

from peacemachine.helpers import urlFilter
from peacemachine.helpers import cut_dateline

from simpletransformers.classification import ClassificationModel
from transformers import MarianMTModel, MarianTokenizer

db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p

prefix = r"D:/Dropbox/ML for Peace/Validation/Colombia Events/"

# load the data
files = [pd.read_excel(prefix+ff) for ff in os.listdir(prefix) if ff.startswith('colombia')]
files = [df for df in files if 'civic_event0' in df.columns]

df = pd.concat(files)
df = df.reset_index(drop=True)

# build combined

# translate titles
model_name = 'opus-mt-ROMANCE-en'
model_name = 'Helsinki-NLP/' + model_name
tokenizer = MarianTokenizer.from_pretrained(model_name)
# see tokenizer.supported_language_codes for choices
model = MarianMTModel.from_pretrained(model_name)
model = model.to('cuda')

for ii in tqdm(df.index):
    src_txt = df.loc[ii, 'Title']
    tokens = tokenizer.prepare_seq2seq_batch([src_txt])
    tokens = tokens.to('cuda')
    translated = model.generate(**tokens)

    result =  tokenizer.batch_decode(translated, skip_special_tokens=True, clean_up_tokenization_spaces=True)

    df.loc[ii, 'title'] = result[0]

# create the combined
for ii in tqdm(df.index):
    df.loc[ii, 'combined'] = df.loc[ii, 'title'] + '. ' + nltk.sent_tokenize(cut_dateline(df.loc[ii, 'Translated_Text']))[0]


# filter the urls
uf = urlFilter('mongodb://ml4pAdmin:ml4peace@192.168.176.240')
filter_list = [uf.filter_url(url) for url in df['URL']]
df = df[filter_list]

# load the model

model_info = db.models.find_one({'model_name': 'civic1'})
label_dict = label_dict = {v:k for k,v in model_info.get('event_type_nums').items()}

model = ClassificationModel('roberta'
                            , "D:/peace-machine/peacemachine/data/finetuned-transformers/ModelOutput/checkpoint-3600-epoch-12"
                            # , num_labels=18
                            , args={
                                'n_gpu': 1
                                , 'eval_batch_size': 24})


# do the predictions
preds, model_outputs = model.predict([tt for tt in df['combined']])

# modify outputs
model_max = [float(max(mo)) for mo in model_outputs]
event_types = [label_dict[ii] for ii in preds]
# apply the cutoff
for ii in range(len(model_max)):
    _et = event_types[ii]
    if model_max[ii] < 9:
        event_types[ii] = '-999'

event_types = [label_dict[ii] for ii in preds]
for ii in range(len(model_max)):
    _et = event_types[ii]
    if model_max[ii] < 7:
        event_types[ii] = '-999'
df['MACHINE_civic_event_type_7'] = event_types


event_types = [label_dict[ii] for ii in preds]
for ii in range(len(model_max)):
    _et = event_types[ii]
    if model_max[ii] < 8:
        event_types[ii] = '-999'
df['MACHINE_civic_event_type_8'] = event_types


event_types = [label_dict[ii] for ii in preds]
for ii in range(len(model_max)):
    _et = event_types[ii]
    if model_max[ii] < 9:
        event_types[ii] = '-999'
df['MACHINE_civic_event_type_9'] = event_types
df['MACHINE_civic_model_max'] = model_max

df = pd.read_csv('D:/Dropbox/ML for Peace/Validation/Colombia Events/machine_colombia2.csv')
# RAI
model = ClassificationModel('roberta'
                            , "D:/Dropbox/peace-machine/peacemachine/data/LAC/CombinedModel_no999"
                            # , num_labels=18
                            , args={
                                'n_gpu': 1
                                , 'eval_batch_size': 24})

model_info = db.models.find_one({'model_name': 'RAI'})
label_dict = label_dict = {v:k for k,v in model_info.get('event_type_nums').items()}

# do the predictions
preds, model_outputs = model.predict([tt for tt in df['combined']])

# modify outputs
model_max = [float(max(mo)) for mo in model_outputs]

event_types = [label_dict[ii] for ii in preds]
# apply the cutoff
for ii in range(len(model_max)):
    _et = event_types[ii]
    if model_max[ii] < 7:
        event_types[ii] = '-999'

df['MACHINE_RAI_event_type_7'] = event_types
df['MACHINE_RAI_model_max'] = model_max

event_types = [label_dict[ii] for ii in preds]
# apply the cutoff
for ii in range(len(model_max)):
    _et = event_types[ii]
    if model_max[ii] < 8:
        event_types[ii] = '-999'

df['MACHINE_RAI_event_type_8'] = event_types
df['MACHINE_RAI_model_max'] = model_max

event_types = [label_dict[ii] for ii in preds]
# apply the cutoff
for ii in range(len(model_max)):
    _et = event_types[ii]
    if model_max[ii] < 9:
        event_types[ii] = '-999'

df['MACHINE_RAI_event_type_9'] = event_types
df['MACHINE_RAI_model_max'] = model_max


df.to_csv('D:/Dropbox/ML for Peace/Validation/Colombia Events/machine_colombia2.csv', index=False)

