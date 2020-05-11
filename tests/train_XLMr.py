import pandas as pd
import numpy as np
np.random.seed(619)
import sklearn
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from tqdm import tqdm
import nltk
import ast
from simpletransformers.classification import ClassificationModel

# ------------------------------------------------------------------------------
# functions

def cut_dateline(string):
    """removes the dateline from the beginning from a string"""
    if ' — ' in string[:40]:
        return string[string.index(' — ')+3:]
    elif '--' in string[:40]:
        return string[string.index('--')+2:]
    elif ' - ' in string[:40]:
        return string[string.index(' - ')+3:]
    # get rid of the CNN dateline
    elif '(CNN)' in string[:40]:
        return string[string.index('(CNN)')+5:]
    elif ': ' in string[:20]:
        return string[string.index(': ')+2:]
    # if no dateline is found, return the same string
    return string


def read_list_text(path, label):
    """reads data generated from rules-based system"""
    # read the file
    mdf = pd.read_csv(path, index_col=0)
    mdf.loc[:, 'labels'] = label
    # convert lists
    mdf = mdf.dropna(axis=0, subset=['text'])
    mdf.loc[:, 'text'] = mdf.text.apply(ast.literal_eval)
    # use only first sentence / cut dateline
    mdf.loc[:, 'first'] = [cut_dateline(ii[0]) for ii in mdf.text]
    # manage the text
    mdf.loc[:, 'title'] = mdf['title'].str.replace('\n', ' ')
    mdf.loc[:, 'first'] = mdf['first'].str.replace('\n', ' ')
    # create a combined title and first sentence
    mdf.loc[:, 'combined'] = mdf['title'].str.cat(mdf['first'])
    # create fold
    mdf.loc[:, 'fold'] = np.random.choice(['train', 'test'], size=len(mdf), p=[.85, .15])
    # return the df
    return mdf.loc[:, ['title', 'first', 'combined', 'labels', 'fold']]


def read_string_text(path, label):
    """reads the data that has the body text as a string"""
    # read the file
    mdf = pd.read_csv(path)
    mdf.loc[:, 'labels'] = label
    # convert lists
    mdf.loc[:, 'text'] = [cut_dateline(ii) for ii in mdf['text']]
    # use only first sentence / cut dateline
    mdf.loc[:, 'first'] = [nltk.sent_tokenize(tt)[0] for tt in mdf.text]
    # manage the text
    mdf.loc[:, 'title'] = mdf['title'].str.replace('\n', ' ')
    mdf.loc[:, 'first'] = mdf['first'].str.replace('\n', ' ')
    # create a combined title and first sentence
    mdf.loc[:, 'combined'] = mdf['title'].str.cat(mdf['first'])
    # create fold
    mdf.loc[:, 'fold'] = np.random.choice(['train', 'test'], size=len(mdf), p=[.85, .15])
    # return the df
    return mdf.loc[:, ['title', 'first', 'combined', 'labels', 'fold']]


#%%
# ------------------------------------------------------------------------------
## import data with list text
violencelethal = read_list_text(r'../data/training-data/violencelethal_filtered.csv', label=0)
arrest = read_list_text(r'../data/training-data/arrest_filtered.csv', label=1)
protest = read_list_text(r'../data/training-data/protest_filtered.csv', label=2)
censor = read_list_text(r'../data/training-data/censor_filtered.csv', label=3)
disaster = read_list_text(r'../data/training-data/disaster_filtered.csv', label=4)
changeelection = read_list_text(r'../data/training-data/changeelection_filtered.csv', label=6)
purge = read_list_text(r'../data/training-data/purge_filtered.csv', label=7)
martiallaw = read_list_text(r'../data/training-data/martiallaw_filtered.csv', label=8)
mobilizesecurity = read_list_text(r'../data/training-data/mobilizesecurity_filtered.csv', label=9)
coup = read_list_text(r'../data/training-data/coup_filtered.csv', label=10)
defamationcase = read_list_text(r'../data/training-data/defamationcase_filtered.csv', label=11)
violencenonlethal = read_list_text(r'../data/training-data/violencenonlethal_filtered.csv', label=12)
threaten = read_list_text(r'../data/training-data/threaten_filtered.csv', label=14)
cooperate = read_list_text(r'../data/training-data/cooperate_filtered.csv', label=15)
raid = read_list_text(r'../data/training-data/raid_filtered.csv', label=16)
changepower = read_list_text(r'../data/training-data/changepower_filtered.csv', label=17)

## import data with string text
censor_s = read_string_text(r'../data/training-data/censor_filtered1.csv', label=3)
legalchange0 = read_string_text(r'../data/training-data/legalchangengo.csv', label=5)
legalchange1 = read_string_text(r'../data/training-data/legalchangespeech.csv', label=5)
legalchange2 = read_string_text(r'../data/training-data/legalchangeassembly.csv', label=5)
changeelection_s = read_string_text(r'../data/training-data/changeelection_filtered1.csv', label=6)
purge_s = read_string_text(r'../data/training-data/purge_filtered1.csv', label=7)
martiallaw_s = read_string_text(r'../data/training-data/martiallaw_filtered1.csv', label=8)
mobilizesecurity_s = read_string_text(r'../data/training-data/mobilizesecurity_filtered1.csv', label=9)
coup_s = read_string_text(r'../data/training-data/coup_filtered1.csv', label=10)
defamationcase_s = read_string_text(r'../data/training-data/defamationcase_filtered1.csv', label=11)
violencenonlethal_s = read_string_text(r'../data/training-data/violencenonlethal_filtered1.csv', label=12)
praise = read_string_text(r'../data/training-data/praise_filtered.csv', label=13)
threaten_s = read_string_text(r'../data/training-data/threaten_filtered1.csv', label=14)
cooperate_s = read_string_text(r'../data/training-data/cooperate_filtered1.csv', label=15)
raid_s = read_string_text(r'../data/training-data/raid_filtered1.csv', label=16)
changepower_s = read_string_text(r'../data/training-data/changepower_filtered1.csv', label=17)

label_dict = {
    0: 'violencelethal'
    , 1: 'arrest'
    , 2: 'protest'
    , 3: 'censor'
    , 4: 'disaster'
    , 5: 'legalchange'
    , 6: 'changeelection'
    , 7: 'purge'
    , 8: 'martiallaw'
    , 9: 'mobilizesecurity'
    , 10: 'coup'
    , 11: 'defamationcase'
    , 12: 'violencenonlethal'
    , 13: 'praise'
    , 14: 'threaten'
    , 15: 'cooperate'
    , 16: 'raid'
    , 17: 'changepower'
}

## manage the data
dfs = [
    violencelethal
    , arrest
    , protest
    , censor
    , censor_s
    , disaster
    , legalchange0
    , legalchange1
    , legalchange2
    , changeelection
    , changeelection_s
    , purge
    , purge_s
    , martiallaw
    , martiallaw_s
    , mobilizesecurity
    , mobilizesecurity_s
    , coup
    , coup_s
    , defamationcase
    , defamationcase_s
    , violencenonlethal
    , violencenonlethal_s
    , praise
    , threaten
    , threaten_s
    , cooperate
    , cooperate_s
    , raid
    , raid_s
    , changepower
    , changepower_s
]

df = pd.concat(dfs)
df = df.reset_index()
# drop doplicates
df.loc[:, 'title'] = df['title'].str.strip()
df = df.drop_duplicates(subset=['title'])

# fix combined
df['combined'] = df['title'] + '. ' + df['first']

# create train/test split
df_title_train = df.loc[df['fold']=='train', ['title', 'labels']]
df_title_train.columns = ['text', 'labels']
df_title_test =  df.loc[df['fold']=='test', ['title', 'labels']]
df_title_test.columns = ['text', 'labels']

df_first_train = df.loc[df['fold']=='train', ['first', 'labels']]
df_first_train.columns = ['text', 'labels']
df_first_test = df.loc[df['fold']=='test', ['first', 'labels']]
df_first_test.columns = ['text', 'labels']

df_both_train = df.loc[df['fold']=='train', ['combined', 'labels']]
df_both_train.columns = ['text', 'labels']
df_both_test = df.loc[df['fold']=='test', ['combined', 'labels']]
df_both_test.columns = ['text', 'labels']

#%%
# ------------------------------------------------------------------------------
# build BERT classifiers
# ------------------------------------------------------------------------------
### weights / sampling
counts = df['labels'].value_counts().sort_index()
weights = [1-(ii/len(df)) for ii in counts]
# TODO: think about sampling to balance data

### first combined
model = ClassificationModel(
            'xlmroberta'
            , 'xlm-roberta-base'
            , num_labels=len(df['labels'].unique())
            , weight=weights
            , use_cuda=True 
            , args={
                   'reprocess_input_data': True
                  , 'overwrite_output_dir': True
                  , 'training_batch_size': 1024
                  , 'evaluate_during_training': True
                  , 'eval_batch_size': 1024
                  , 'num_train_epochs': 50
                  , 'use_early_stopping': True
                  , 'early_stopping_patience': 5
                  , 'output_dir': r'../data/models/XLMr-ModelOutput'
                  , 'cache_dir': r'../data/models/XLMr-ModelOutput'}) 

if __name__ == "__main__":
    model.train_model(train_df=df_both_train, eval_df=df_both_test)

    # Evaluate the model
    result, model_outputs, wrong_predictions = model.eval_model(df_both_test)

    y_t = df_both_test.labels
    y_hat = [np.argmax(a) for a in model_outputs]
    print(sklearn.metrics.classification_report(y_true=y_t, y_pred=y_hat))