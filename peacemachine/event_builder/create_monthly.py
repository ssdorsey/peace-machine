import pandas as pd
import numpy as np
from tqdm import tqdm

import pymongo

cl = pymongo.MongoClient()
db = cl.ml4p

events = pd.read_csv('D:/eventss.csv')
events = events[events['bad_location'].notnull()]

# events2 = pd.read_csv("C:/Users/spenc/Downloads/events_export.csv")
# events2 = events2[events2['bad_location'].notnull()]

# events3 = pd.read_csv("E:/Dropbox/ML for Peace/Spencer_Code/Clean/Data/events_preliminary.csv")
# events3 = events3.rename(columns={'location':'bad_location'})
# events3 = events3[events3['bad_location'].notnull()]

# events4 = 

# events = pd.concat([events, events2, events3])

# events = events.drop_duplicates(subset='url')
# events = events.drop_duplicates(subset=['title'])

# fix mis-labeled countries TODO: fix them in the db!!
events['bad_location'] = events['bad_location'].replace({'Ecudaor':'Ecuador'})

events = events[events['date_publish'].notnull()]

events['date_publish'] = pd.to_datetime(events['date_publish'])
events['year'] = [int(str(dd).split('-')[0]) for dd in events['date_publish']]
events['month'] = [int(str(dd).split('-')[1]) for dd in events['date_publish']]

df = events

countries = ['Kenya', 'Nigeria', 'Tanzania', 'Mali', 'Serbia', 'Georgia', 'Ecuador', 'Colombia']

e_types = df['event_type'].unique()

def monthly_counts_flat(country):
    hold_country = []
    country_df = df[df['bad_location'].str.lower()==country.lower()]
    for year in tqdm(range(2000, 2021)):
        for month in range(1, 13):
            hold_series = pd.Series()
            hold_series['year'] = year
            hold_series['month'] = month
            hold_series['location'] = country

            sub_df = country_df[(country_df['year']==year) & 
                    (country_df['month']==month)]

            for e_type in e_types:
                hold_series[e_type] = len(sub_df[sub_df['event_type']==e_type])

            hold_country.append(hold_series)

    country_df = pd.DataFrame(hold_country)
    # cut rows
    country_df = country_df.iloc[:-9]
    country_df.to_csv(f'data/counts/{country.lower()}_counts.csv') 


for country in countries:
    print('Starting: ' + country)
    monthly_counts_flat(country)
    print('Finished: ' + country)


# # TODO: Fix Colombia and Ecuador misspellings!!

# def convert_datetime

# def monthly_counts_db(country):
#     hold_country = []
#     for year in tqdm(range(2000, 2021)):
#         for month in range(1, 13):
#             hold_series = pd.Series()
#             hold_series['year'] = year
#             hold_series['month'] = month
#             hold_series['location'] = country

#             for e_type in e_types:
#                 _count = db.events.count_documents(
#                     {
#                         {'bad_location': {'$toLower': country.lower()}},
#                         {{'$split': ['$date_publish', '-']}[0]: str(year)},
#                         {{'$split': ['$date_publish', '-']}[1]: '{:02d}'.format(month)}
#                     }
#                 )
#                 hold_series[e_type] = _count

#             hold_country.append(hold_series)

#     country_df = pd.DataFrame(hold_country)
#     # cut rows
#     country_df = country_df.iloc[:-9]
#     country_df.to_csv(f'data/counts/{country.lower()}_counts.csv') 


# ------------------------
# DELETE THIS
# ------------------------
# replace data before 2016 for Kenya, Tanzania, Nigeria, Mali

# kenya_old = pd.read_csv('/home/spenc/Downloads/counts/kenya_counts.csv', index_col=0)
# kenya_new = pd.read_csv('/home/spenc/Dropbox/peace-machine/peacemachine/data/counts/kenya_counts.csv', index_col=0)
# pd.concat([kenya_old.iloc[:194, :], kenya_new.iloc[194:, :]]).to_csv('/home/spenc/Downloads/counts/kenya_counts.csv')

# nigeria_old = pd.read_csv('/home/spenc/Downloads/counts/nigeria_counts.csv', index_col=0)
# nigeria_new = pd.read_csv('/home/spenc/Dropbox/peace-machine/peacemachine/data/counts/nigeria_counts.csv', index_col=0)
# pd.concat([nigeria_old.iloc[:194, :], nigeria_new.iloc[194:, :]]).to_csv('/home/spenc/Downloads/counts/nigeria_counts.csv')

# tanzania_old = pd.read_csv('/home/spenc/Downloads/counts/tanzania_counts.csv', index_col=0)
# tanzania_new = pd.read_csv('/home/spenc/Dropbox/peace-machine/peacemachine/data/counts/tanzania_counts.csv', index_col=0)
# pd.concat([tanzania_old.iloc[:194, :], tanzania_new.iloc[194:, :]]).to_csv('/home/spenc/Downloads/counts/tanzania_counts.csv')

# mali_old = pd.read_csv('/home/spenc/Downloads/counts/mali_counts.csv', index_col=0)
# mali_new = pd.read_csv('/home/spenc/Dropbox/peace-machine/peacemachine/data/counts/mali_counts.csv', index_col=0)
# pd.concat([mali_old.iloc[:194, :], mali_new.iloc[194:, :]]).to_csv('/home/spenc/Downloads/counts/mali_counts.csv')

