import os
import re
from tqdm import tqdm 

import pymongo

cl = pymongo.MongoClient()
db = cl.ml4p


def convert_path(path, target_path_prefix):
    """
    converts a C:/ path to an F:/ path
    :param path: The path from news-please entry that needs to be fixed
    :param target_path_prefix: the first part of the path we want
    :return: string with the modified path
    """
    # if we already have the starting path we want just return
    if path.startswith(target_path_prefix[:1]): # TODO: check this number
        return path
    # if we need to change it
    np = re.sub(r'(.*)news-please-repo/+data/+', target_path_prefix, path)
    np = np.replace('\\', '/')
    np = np.replace('//', '/')
    return np


def save_html(html, path):
    """
    function to save html code that is in a mongo doc
    :param html:
    """
    new_path = convert_path(path=path, target_path_prefix='F:/news-please-repo/data/')
    # check to see if the path exists
    directory = os.path.dirname(new_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # write the html
    with open(new_path, 'w', encoding='utf-8') as _file:
        _file.write(html)

for _doc in tqdm(db.articles.find()):
    if 'html' in _doc:
        save_html(_doc['html'], _doc['localpath'])

print('NOW DELETING HTML FROM ARTICLES DB')
db.articles.update({}, {'$unset': {'html':1}}, multi=True)
