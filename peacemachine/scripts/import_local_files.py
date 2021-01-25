import os
import os.path
import json
import dateparser

from p_tqdm import p_umap

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

db = MongoClient('mongodb://ml4pAdmin:ml4peace@192.168.176.240').ml4p

def check_insert(_file):


    with open(_file, 'r', encoding='utf-8') as ff:
        fd = json.load(ff)

    # check date format
    try:
        if isinstance(fd['date_publish'], str):
            fd['date_publish'] = dateparser.parse(fd['date_publish'])
    except:
        print('DATE ISSUE')
        return

    try:
        if fd['date_publish']:
            colname = f"articles-{fd['date_publish'].year}-{fd['date_publish'].month}"
        else:
            colname = 'articles-nodate'

        db[colname].insert_one(fd)

    except DuplicateKeyError:
        pass


if __name__ == "__main__":
    _dir = 'H:\\TEMP'

    files = []
    for dirpath, dirnames, filenames in os.walk(_dir):
        for filename in [f for f in filenames if f.endswith(".json")]:
            files.append(os.path.join(dirpath, filename))

    p_umap(check_insert, files, num_cpus=8)
