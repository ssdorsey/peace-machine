# import packages
import re
import numpy as np
import pandas as pd
from tqdm import tqdm
import sklearn
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from simpletransformers.classification import ClassificationModel
import nltk


pd.options.display.max_colwidth = 100

np.random.seed(619)

df = pd.read_csv("../data/LAC/LAC.csv", encoding='utf-8')

# drop na
df = df.dropna(subset=['article_body'])

# get rid of â€”
df.loc[:, 'article_title'] = df['article_title'].str.replace('â€”', '')
df.loc[:, 'article_title'] = df['article_title'].str.replace('â€™', "'")
df.loc[:, 'article_body'] = df['article_body'].str.replace('â€”', '')
df.loc[:, 'article_body'] = df['article_body'].str.replace('â€™', "'")

# helper functions
def cut_dateline(_string):
    """removes the dateline from the beginning from a string"""
    if ' — ' in _string[:30]:
        return _string[_string.index(' — ')+3:]
    elif '--' in _string[:30]:
        return _string[_string.index('--')+2:]
    elif ' - ' in _string[:30]:
        return _string[_string.index(' - ')+3:]
    elif ': ' in _string[:20]:
        return _string[_string.index(': ')+2:]
    elif bool(re.search(r'(\(.*?\)\s)', _string[:30])):
        res = re.search(r'(\(.*?\)\s)', _string[:30])
        return _string[res.end(): ]        
    # special for authors + Reuters
    elif _string.startswith('By '):
        if bool(re.search(r'(\(.*?\)\s)', _string[:70])):
            res = re.search(r'(\(.*?\)\s)', _string[:70])
            return _string[res.end() + 2: ]
    # if no dateline is found, return the same string
    return _string.strip()

def get_first_sentence(_string):
    return nltk.sent_tokenize(cut_dateline(_string))[0]

# pull first sentence 
df.loc[:, 'first_sentence'] = [get_first_sentence(tt).strip() for tt in tqdm(df['article_body'])]

# isolate the event labels
labels = sorted([str(at) for at in df['action_type'].unique()])
label_dict = dict(zip(labels, range(len(labels))))

df.loc[:, 'action_type'] = [label_dict[at] for at in df['action_type']]

# unwind and make the text separate lines
df1 = df[['article_title', 'action_type']]
df1.columns = ['text', 'labels']
df2 = df[['first_sentence', 'action_type']]
df2.columns = ['text', 'labels']
df_stacked = pd.concat([df1, df2])

# make a combined verion
df.loc[:, 'combined'] = df['article_title'] + ' ' + df['first_sentence']
df_combined = df[['combined', 'action_type']]
df_combined.columns = ['text', 'labels']

# split into train/test/validate
df_stacked.loc[: , 'split'] = np.random.choice([0,1,2], len(df_stacked), p=[.8, .1, .1])
train_stacked = df_stacked.loc[df_stacked.split==0 ,['text', 'labels']]
train_stacked = train_stacked[train_stacked['labels']!=0]
test_stacked = df_stacked.loc[df_stacked.split==1 ,['text', 'labels']]
validate_stacked = df_stacked.loc[df_stacked.split==2 ,['text', 'labels']]

df_combined.loc[: , 'split'] = np.random.choice([0,1,2], len(df_combined), p=[.8, .1, .1])
train_combined = df_combined.loc[df_combined.split==0 ,['text', 'labels']]
train_combined = train_combined[train_combined['labels']!=0]
test_combined = df_combined.loc[df_combined.split==1 ,['text', 'labels']]
validate_combined = df_combined.loc[df_combined.split==2 ,['text', 'labels']]

if __name__ == "__main__":

    # model = ClassificationModel(
    #         'roberta'
    #         , 'roberta-base'
    #         , num_labels=len(labels)
    #         , use_cuda=True 
    #         , cuda_device=0
    #         , args={'reprocess_input_data': True
    #               , 'overwrite_output_dir': True
    #               , 'training_batch_size': 512
    #               , 'eval_batch_size': 512
    #               , 'num_train_epochs': 30
    #               , 'output_dir': r'..\data\LAC\StackedModel_no999'
    #               , 'cache_dir': r'..\data\LAC\StackedModel_no999'
    #               , 'evaluate_during_training': True
    #               , 'use_early_stopping': True}) 

    # model.train_model(train_stacked, eval_df=validate_stacked)

    model = ClassificationModel(
            'xlmroberta'
            , 'xlm-roberta-base'
                , num_labels=len(labels)
                , use_cuda=True 
                , cuda_device=0
                , args={'reprocess_input_data': True
                    , 'overwrite_output_dir': True
                    , 'training_batch_size': 512
                    , 'eval_batch_size': 512
                    , 'num_train_epochs': 30
                    , 'output_dir': r'..\data\LAC\StackedXLMR_no999'
                    , 'cache_dir': r'..\data\LAC\StackedXLMR_no999'
                    , 'evaluate_during_training': True
                    , 'use_early_stopping': True}) 
        
    model.train_model(train_stacked, eval_df=validate_stacked)