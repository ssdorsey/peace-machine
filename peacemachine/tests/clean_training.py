import pandas as pd
import numpy as np
import re
import ast
import getpass

from tqdm import tqdm
from simpletransformers.classification import ClassificationModel
import plotly.graph_objects as go
import sklearn
from pymongo import MongoClient

from peacemachine import helpers

if getpass.getuser() in ['Batan', 'spenc']: #TODO convert this over to a command-line read
    uri = 'mongodb://ml4pAdmin:ml4peace@192.168.176.240'
else:
    uri = 'mongodb://ml4pAdmin:ml4peace@vpn.ssdorsey.com'

db = MongoClient(uri).ml4p

np.random.seed(619)

spec_re = re.compile(r"(\n|\r|\\n|\\|\')")

# df = pd.read_csv(r"D:\Dropbox\ML for Peace\Data\Training_data\New_Codebook_Data\consolidated.csv")

# # deal with the lists
# for ii in df.index:
#     text = str(df.loc[ii, 'text'])
#     if text.startswith('['):
#         _list = ast.literal_eval(text)
#         _list = [tt.strip() for tt in _list]
#         new_text = ' '.join(_list)
#         df.loc[ii, 'text'] = new_text

# insert into db 
# for ii in tqdm(df.index):
#     doc = df.loc[ii].to_dict()
#     doc['status'] = 'approved'
#     db['civic-training'].insert_one(doc)

# pull from DB
docs = [doc for doc in db['civic-training'].find({'status': 'approved'}).sort([('_id', 1)])]
df = pd.DataFrame(docs)
df = df.drop(columns=['_id'])

# # do one other bit of clearing
for ii in df.index:
    text = str(df.loc[ii, 'text'])
    new_text = helpers.cut_dateline(text)
    new_text = spec_re.sub('', new_text)
    df.loc[ii, 'text'] = new_text

# build the combined
for ii in df.index:
    df.loc[ii, 'combined'] = helpers.build_combined(df.loc[ii].to_dict())

# build the label_dict 
labels = sorted(list(df['event'].unique()))

label_dict = dict(zip(labels, range(len(labels))))

# split train/test
df['labels'] = [label_dict[ii] for ii in df['event']]

df['split'] = np.random.choice([0,1], size=len(df), p=[0.85, 0.15])

train = df.loc[df['split']==0, ['combined', 'labels']]
test = df.loc[df['split']==1, ['combined', 'labels']]

train = train.rename(columns={'combined': 'text'})
test = test.rename(columns={'combined': 'text'})

# set up the model
counts = df['labels'].value_counts().sort_index()
weights = [1-(ii/len(df)) for ii in counts]


# if __name__ == "__main__":

#     model = ClassificationModel(
#                 'roberta'
#                 , 'roberta-base'
#                 , num_labels=len(df['labels'].unique())
#                 , weight=weights
#                 , use_cuda=True 
#                 , args={'reprocess_input_data': True
#                     , 'overwrite_output_dir': True
#                     , 'training_batch_size': 64
#                     , 'eval_batch_size': 64
#                     , 'num_train_epochs': 30
#                     , 'num_workers': 0
#                     , 'output_dir': r'data/finetuned-transformers/ModelOutput'
#                     , 'cache_dir': r'data/finetuned-transformers/ModelOutput'}) 

#     model.train_model(train)

model = ClassificationModel(
    'roberta', 
    r"D:\peace-machine\peacemachine\data\finetuned-transformers\ModelOutput\checkpoint-4500-epoch-15",
    num_labels=len(df['labels'].unique()),
    args={
        'eval_batch_size': 64
    }
)

# Evaluate the model
result, model_outputs, wrong_predictions = model.eval_model(test)

y_t = test.labels
y_hat = [np.argmax(a) for a in model_outputs]
print(sklearn.metrics.classification_report(y_true=y_t, y_pred=y_hat))

    # # func for heatmap
def prep_heatmap(y, y_hat, label_dict):
    accuracy_df = pd.DataFrame({'y': y, 'y_hat':y_hat})
    n_categories = len(label_dict.keys())

    confusion = np.zeros((n_categories, n_categories))
    confusion_normal = np.zeros((n_categories, n_categories))

    # Go through test and record which are correctly guessed
    for i in range(len(accuracy_df)):
        actual = accuracy_df['y'].iloc[i]
        predicted = accuracy_df['y_hat'].iloc[i]
        confusion[actual, predicted] += 1

    # Normalize by dividing every row by its sum
    for i in range(n_categories):
        if confusion[i].sum() > 0:
            confusion_normal[i] = confusion[i] / confusion[i].sum()

    confusion_normal = np.nan_to_num(confusion_normal, nan=0)

    return {'confusion': confusion, 'confusion_norm': confusion_normal}

def draw_heatmap(y, y_hat, label_dict): 
    hm_data = prep_heatmap(y, y_hat, label_dict)
    hovertext = list()
    events = range(len(label_dict.keys()))
    for yy in events:
        hovertext.append(list())
        for xx in events:
            hovertext[-1].append(f'y: {label_dict[yy]}<br />'
                                    f'ŷ: {label_dict[xx]}<br />'
                                    f'%: {(hm_data["confusion_norm"][yy][xx])*100}<br />'
                                    f'Count: {hm_data["confusion"][yy][xx]}')

    fig = go.Figure()
    fig.add_trace(
        go.Heatmap(
                    z=hm_data['confusion_norm'],
                    x=list(label_dict.values()),
                    y=list(label_dict.values()),
                    hoverongaps = False, 
                    hoverinfo='text',
                    text=hovertext, 
                    colorscale='OrRd'
                    

        )
    )

    fig.update_layout(
        autosize=False,
        width=900,
        height=700,
        margin=dict(
            l=50,
            r=20,
            b=200,
            t=20,
            pad=4
        ), 
        template='plotly_white', 

    )
    fig.update_xaxes(tickangle=-45)
    return fig

ff = draw_heatmap(y_t, y_hat, {v:k for k, v in label_dict.items()})

print(sklearn.metrics.classification_report(y_true=y_t, y_pred=y_hat))
