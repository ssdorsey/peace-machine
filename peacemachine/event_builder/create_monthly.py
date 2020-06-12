import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import pandas as pd
from pymongo import MongoClient

db = MongoClient('mongodb://ml4pAdmin:ml4peace@devlab-server').ml4p

e_types = [
    '-999',
    'threaten',
    'protest',
    'changepower',
    'purge',
    'changeelection',
    'cooperate',
    'violencelethal',
    'legalchange',
    'censor',
    'violencenonlethal',
    'praise',
    'arrest',
    'disaster',
    'mobilizesecurity',
    'raid',
    'coup',
    'defamationcase',
    'martiallaw'
]

countries = [fn.split('_')[1][:-4] for fn in os.listdir('../data/domains') if fn.startswith('domains_')]
countries.remove('international')
# countries = ['Colombia']

month_starts = []
date = datetime(2000, 1, 1)
while date < (datetime.today() - relativedelta(months=1)):
    date += relativedelta(months=1)
    month_starts.append(date)


def monthly_counts_flat(country):
    hold_country = []

    for m_start in tqdm(month_starts):
        hold_series = pd.Series()
        hold_series['year'] = m_start.year
        hold_series['month'] = m_start.month
        hold_series['location'] = country

        col_name = f'{m_start.year}-{m_start.month}-events'

        for e_type in e_types:
            hold_series[e_type] = db[col_name].count_documents(
                {
                    'bad_location': country,
                    'event_type': e_type,
                    'exclude': {'$ne': True},
                }
            )
            # print(hold_series)

        hold_country.append(hold_series)

    country_df = pd.DataFrame(hold_country)

    country_df.to_csv(f'../data/counts/{country.lower()}_counts.csv')
    country_df.to_csv(f'../../../Ml for Peace/Counts_Civic/{country.lower()}_counts.csv')
    

if __name__ == "__main__":
    for country in countries:
        print('STARTING: ' + country)
        monthly_counts_flat(country)
