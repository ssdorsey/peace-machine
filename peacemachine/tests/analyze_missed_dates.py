from tqdm import tqdm
import pandas as pd
import plotly.graph_objects as go
from pymongo import MongoClient

if sys.platform=='win32' or os.environ['USER'] != 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p

available_countries = [fn.split('_')[1].split('.')[0] for fn in os.listdir('../data/domains') 
    if fn.startswith('domains_') and not fn.endswith('international.txt')]

domain_locs = {}
for ac in available_countries:
    with open(f'../data/domains/domains_{ac}.txt', 'r') as _file:
        domains = [dd.strip() for dd in _file.readlines()]
    for dd in domains:
        domain_locs[dd] = ac
domains = [k for k in domain_locs.keys()]
        
df = pd.DataFrame({'domain': domains})

for ii in tqdm(df.index):
    domain = df.loc[ii, 'domain']
    df.loc[ii, 'count'] = db['articles_nodate'].count_documents({'source_domain': domain})

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df['domain'],
    y=df['count']
))


db['articles_nodate'].find(
    {
        'source_domain': 'pravda.com.ua', 
        'url': {'$not': {'$regex': '\/profile\/|\/authors\/'}}
    }
)[100]

