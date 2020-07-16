#%%
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from p_tqdm import p_umap
from pymongo import MongoClient

if os.getlogin() == 'Batan':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p
if os.getlogin() == 'devlab':
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@localhost').ml4p
else:
    db = MongoClient('mongodb://ml4pAdmin:ml4peace@vpn.ssdorsey.com').ml4p

#%%
def keep_url(url):
    # check to see if it's in the DB in any form
    # if (bool(db.articles.find_one({'url': url})) or 
    #     bool(db.articles.find_one({'url': url+'/'}))):
    #     return False
    # check to see if it's in the missing date DB
    # if (bool(db['articles_nodate'].find_one({'url': url})) or
    #     bool(db['articles_nodate'].find_one({'url': url+'/'}))):
    #     return False
    if db.articles.find({'url': url}).limit(1).count() > 0:
        return True
    return True

#%%
# all wayback links
# wb_files = [fn for fn in os.listdir('data/wayback_urls/') if fn.endswith('_urls.txt')]

# wb = []
# for fn in tqdm(wb_files):
#     try:
#         with open(f'data/wayback_urls/{fn}', 'r') as _file:
#             wb.append([ll.strip() for ll in _file.readlines()])
#     except:
#         print('ERROR!!')

# wb = pd.concat([pd.Series(ll) for ll in wb], ignore_index=True)
# wb = wb.drop_duplicates()
# wb = pd.DataFrame({'url': wb})
# wb['download_via'] = 'wayback'

# # filter out what I already have
# wb = wb[[keep_url(uu) for uu in tqdm(wb['url'])]]

wb = pd.read_csv('00_wayback_master.csv')


#%%
def read_gdelt(_file):
    return pd.read_csv(_file, squeeze=True)

if __name__ == "__main__":
    # all gdelt links
    gdelt_files = ['D:/temp/urls/'+fn for fn in os.listdir('D:/temp/urls/') if fn.endswith('.csv')]

    gdelt = p_umap(read_gdelt, gdelt_files, num_cpus=12)

    gdelt = pd.concat(gdelt, ignore_index=True)
    gdelt = gdelt.drop_duplicates()
    print(len(gdelt))
    gdelt = pd.DataFrame({'url': gdelt})
    gdelt['download_via'] = 'gdelt'

    # #%%
    # combine and filter
    urls = pd.concat([wb, gdelt])
    urls = urls.drop_duplicates(subset=['url'])

    # make 15 folds

    urls['fold'] = np.random.randint(1, 16, len(urls))

    urls.to_csv('all_urls.csv', index=False)
# %%
