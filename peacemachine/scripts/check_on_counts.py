import os
import getpass
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.express as px
from tqdm import tqdm

from pymongo import MongoClient

if getpass.getuser() in ['Batan', 'spenc']: #TODO convert this over to a command-line read
    uri = 'mongodb://ml4pAdmin:ml4peace@192.168.176.240'
else:
    uri = 'mongodb://ml4pAdmin:ml4peace@vpn.ssdorsey.com'

db = MongoClient(uri).ml4p


def graph_counts(domain, include=False):
    dates = pd.date_range(start='2010-1-1', end=pd.Timestamp.today()+relativedelta(months=1), freq='m')
    counts = []

    for date in tqdm(dates):

        if include:
            count = db[f'articles-{date.year}-{date.month}'].count_documents(
                {
                    'source_domain': domain,
                    # 'include': True
                }
            )
        else:
            count = db[f'articles-{date.year}-{date.month}'].count_documents(
                {
                    'source_domain': domain,
                }
            )            

        counts.append(count)


    df = pd.DataFrame({'date': dates, 'count': counts})
    fig = px.line(df, x="date", y="count", title=f'{domain} article count over time')
    fig.show()


def graph_counts_countries(iso_code, include=False):
    doms = db['sources'].find({'primary_location': iso_code.upper()})
    doms = [doc['source_domain'] for doc in doms]

    for dom in doms:
        graph_counts(dom, include)


def graph_sections(source_domain, num_sections=30, drop_nums=True):
    """
    :param sd: source_domain to check section counts
    """
    urls = []
    cols = [col for col in db.list_collection_names() if col.startswith('articles-')]
    for col in cols:
        urls += [doc['url'] for doc in db[col].find({'source_domain': source_domain})]

    m_sections = []
    for url in urls:
        url = url[url.index(source_domain)+len(source_domain): ]
        sections = [sec for sec in url.split('/')[:-1] if sec]
        m_sections += sections
    sec = pd.Series(m_sections)
    counts = pd.DataFrame(sec.value_counts())
    counts = counts.reset_index()
    counts = counts.rename(columns={'index':'section', 0: 'count'})
    
    if drop_nums:
        counts = counts[~counts['section'].str.isdigit()]
        counts = counts.reset_index(drop=True)
    else:
        counts['section'] = [f'/{ii}' for ii in counts['section']]

    fig = px.bar(counts.iloc[:num_sections], x='section', y='count', title=f'{source_domain} section counts')
    fig.show()

graph_sections('assabah.ma', drop_nums=False)

graph_counts('assabah.ma', include=False)
graph_counts('dakaractu.com', include=True)
graph_counts_countries('SEN')

