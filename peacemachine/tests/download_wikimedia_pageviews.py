import os
import urllib.request
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

index = 'https://dumps.wikimedia.org/other/pageviews/2020/2020-05/'

index_html = urllib.request.urlopen(index).read()
soup = bs(index_html)

all_links = [a['href'] for a in soup.find_all('a') if a['href'].endswith('.gz')]

already_downloaded = [fn for fn in os.listdir('../data/wikipedia/pageviews') if fn.endswith('.gz')]

for link in tqdm(all_links):
    if link not in already_downloaded:
        url = index+link
        try:
        	urllib.request.urlretrieve(url, f'../data/wikipedia/pageviews/{link}')
        except:
        	print('ERROR ON: '+url)
        	
    
