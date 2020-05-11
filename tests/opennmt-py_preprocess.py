import os
from tqdm import tqdm
import numpy as np

np.random.seed(619)

data_path = 'data/translation/ES/archives/'

en_paths = [ff for ff in os.listdir(data_path) if ff.endswith('.en')]
collections = [ff.split('.en-es')[0] for ff in en_paths]

# drop UN data for now, language is very different
collections = [ff for ff in collections if ff != 'UNPC']


data = {}
for cc in tqdm(collections):
    
    print('Loading: ', cc)

    with open(data_path+cc+'.en-es.en', 'r') as _file:
        en = [ll.strip() for ll in _file.readlines()]
    
    with open(data_path+cc+'.en-es.es', 'r') as _file:
        es = [ll.strip() for ll in _file.readlines()]

    if len(en) != len(es):
        print('DIFFERENT LENGTHS!!!!!')

    # strip url-only lines
    if cc == 'TED2013':
        en = [ll for ll in en if not ll.startswith('http://')]
        es = [ll for ll in es if not ll.startswith('http://')]

    data[cc] = {'en': en, 'es': es}

for k, v in data.items():
    print(k)
    print(v['en'][0])
    print(v['es'][0])
    print(' ')
    print(v['en'][1])
    print(v['es'][1])
    print('-----------------------------------------------------------')



all_en = []
all_es = []
for k, v in data.items():
    all_en += v['en']
    all_es += v['es']

folds = np.random.random(len(all_en))

valid_start =  1 - ((5000/len(all_en)) * 100)

test_start = valid_start - ((10000/len(all_en)) * 100)

train_en = [sent for nn, sent in enumerate(all_en) if folds[nn] < test_start]
train_es = [sent for nn, sent in enumerate(all_es) if folds[nn] < test_start]

test_en = [sent for nn, sent in enumerate(all_en) if folds[nn] >= test_start and folds[nn] < valid_start]
test_es = [sent for nn, sent in enumerate(all_es) if folds[nn] >= test_start and folds[nn] < valid_start]

valid_en = [sent for nn, sent in enumerate(all_en) if folds[nn] >= valid_start]
valid_es = [sent for nn, sent in enumerate(all_es) if folds[nn] >= valid_start]

datas = [train_en, train_es, valid_en, valid_es, test_en, test_es]
names = ['train_en', 'train_es', 'valid_en', 'valid_es', 'test_en', 'test_es']

for ii in range(len(datas)):
    with open(f'data/translation/ES/{names[ii]}.txt', 'w') as _file:
        for ll in datas[ii]:
            _file.write(ll+'\n')


