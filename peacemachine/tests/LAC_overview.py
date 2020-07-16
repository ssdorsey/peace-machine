# import packages
import re
import pickle
import numpy as np
import pandas as pd
from tqdm import tqdm
import sklearn
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import plotly.graph_objects as go
from simpletransformers.classification import ClassificationModel

import os
os.chdir('peacemachine/tests')

# set seed for splitting data
np.random.seed(619)

# data info
events = range(25)
label_dict = pickle.load( open( "../data/LAC/label_dict.p", "rb" ) )
label_dict = {v:k for k,v in label_dict.items()}

# import data
raw = pd.read_csv('../data/LAC/LAC.csv')
validate_stacked = pd.read_csv('../data/LAC/validate_stacked.csv')
validate_combined = pd.read_csv('../data/LAC/validate_combined.csv')


def prep_heatmap(y, y_hat):
    accuracy_df = pd.DataFrame({'y': y, 'y_hat':y_hat})
    n_categories = len(events)
    all_categories = events
    all_cat_names = [label_dict[ii] for ii in all_categories]

    confusion = np.zeros((n_categories, n_categories))
    confusion_normal = np.zeros((n_categories, n_categories))

    num_mapping = dict(zip(all_categories, range(n_categories)))

    # Go through test and record which are correctly guessed
    for i in range(len(accuracy_df)):
        actual = accuracy_df['y'].iloc[i]
        predicted = accuracy_df['y_hat'].iloc[i]
        confusion[num_mapping[actual], num_mapping[predicted]] += 1

    # Normalize by dividing every row by its sum
    for i in range(n_categories):
        confusion_normal[i] = confusion[i] / confusion[i].sum()

    confusion_normal = np.nan_to_num(confusion_normal, nan=0)

    return {'confusion': confusion, 'confusion_norm': confusion_normal}

def draw_heatmap(y, y_hat): 
    hm_data = prep_heatmap(y, y_hat)
    hovertext = list()
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
                    x=[label_dict[ii] for ii in range(len(label_dict))],
                    y=[label_dict[ii] for ii in range(len(label_dict))],
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
        template='plotly_white'
    )
    fig.update_xaxes(tickangle=-45)
    fig.show()

# check out what we have
raw_counts = raw['action_type'].value_counts()
valid_counts = validate_combined['labels'].value_counts()
valid_counts.index = [label_dict[ii] for ii in valid_counts.index]

fig = go.Figure()
fig.add_trace(go.Bar(x=raw_counts.index, y=raw_counts, name='All training',
                     hovertemplate = "%{x} <br>%{y}"))
fig.add_trace(go.Bar(x=valid_counts.index, y=valid_counts, name='Validation', 
                     hovertemplate = "%{x} <br>%{y}"))

fig.update_layout(
    autosize=False,
    width=900,
    height=500,
    margin=dict(
        l=50,
        r=20,
        b=200,
        t=20,
        pad=4
    ), 
    template='plotly_white'
)
fig.update_xaxes(tickangle=-45)
fig.show()

## Results

"""
I took three different approaches to training the classifier. 
In the first (stacked), I treat each title and first sentence as seperate observations.
In the second (combined), I treat combine the title and sentence into a single sequence.
In the third (first_sent), I use only the first sentence
"""

### Stacked

# load the model
model = ClassificationModel('roberta'
                            , '../data/LAC/StackedModel'
                            , num_labels=25
                            , args={
                                'n_gpu':1
                                ,'eval_batch_size':768})

# run on the validation data
result, model_outputs, wrong_predictions = model.eval_model(validate_stacked)

# check out the results
y = validate_stacked.labels
y_hat = [np.argmax(a) for a in model_outputs]

print(sklearn.metrics.classification_report(y_true=y, y_pred=y_hat))

# Here's an interactive heat map


# ----------------------------------------------------------------------------------------------------------------------
# trained without -999
# ----------------------------------------------------------------------------------------------------------------------
# combined all the training -999 as well
train_stacked = pd.read_csv('../data/LAC/train_stacked.csv')
validate_stacked = pd.concat([validate_stacked, train_stacked[train_stacked['labels']==0]])

# load the model
model = ClassificationModel('roberta'
                            , '../data/LAC/StackedModel_no999'
                            , num_labels=25
                            , args={
                                'n_gpu':1
                                ,'eval_batch_size':768})

# threshold for 999
preds, model_outputs = model.predict(validate_stacked['text'])
# modify outputs
model_max = [float(max(mo)) for mo in model_outputs]

for ii in range(len(model_max)):
    if model_max[ii] < 7:
        preds[ii] = 0

# check out the results
y = validate_stacked.labels
y_hat = [np.argmax(a) for a in model_outputs]

print(sklearn.metrics.classification_report(y_true=y, y_pred=y_hat))

draw_heatmap(y, y_hat)

model.predict(["US tech giant Nvidia in biggest ever deal with $6.9bn takeover of Israel's Mellanox"])

validate_stacked['y_hat'] = preds

validate_stacked[validate_stacked['labels']==0].head(5)

# combined all the training -999 as well
train_stacked = pd.read_csv('../data/LAC/train_stacked.csv')
validate_stacked = pd.concat([validate_stacked, train_stacked[train_stacked['labels']==0]])

# load the model
model = ClassificationModel('xlmroberta'
                            , '../data/LAC/StackedXLMR_no999'
                            , num_labels=25
                            , args={
                                'n_gpu':1
                                ,'eval_batch_size':768})
preds, model_outputs = model.predict(validate_stacked['text'])

preds_cut = preds
# modify outputs
model_max = [float(max(mo)) for mo in model_outputs]
# threshold for 999
for ii in range(len(model_max)):
    if model_max[ii] < 6:
        preds_cut[ii] = 0

# check out the results
y = validate_stacked.labels
y_hat = preds_cut

print(sklearn.metrics.classification_report(y_true=y, y_pred=y_hat))

draw_heatmap(y, y_hat)

valid_view = validate_stacked
valid_view['y'] = [label_dict[ii] for ii in valid_view['labels']]
valid_view['y_hat'] = [label_dict[ii] for ii in preds]
valid_view.drop
pd.options.display.max_colwidth =200

valid_view[(valid_view['y']=='-999') & (valid_view['y_hat']!='-999')].sample(5)


