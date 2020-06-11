import os
import time
import sys
import io
import tarfile
from tqdm import tqdm
import pandas as pd
from joblib import Parallel, delayed

from nytextract import parse_xml
# ----------------------------------------------------------------------------------------
# read in the compressed data
# ----------------------------------------------------------------------------------------

def extract_xmls(tar_bytes):
    """
    extract the .xml from the .tgz converted into bytes
    """
    hold_xmls = []
    tar2 = tarfile.open(fileobj=tar_bytes)
    tar_xmls = [ii for ii in tar2 if ii.name.endswith('.xml')]
    for tar_xml in tar_xmls:
        my_xml = tar2.extractfile(tar_xml)
        my_flo = io.BytesIO(my_xml.read()).read()
        hold_xmls.append(my_flo)
    tar2.close()
    return hold_xmls


def prep_data(tar_url):
    """
    Open the master tar file and prep the items
    """
    # open master
    tar = tarfile.open(tar_url, 'r:gz')
    # filter the files
    items = [ii for ii in tar if ii.name.endswith('.tgz')]
    # open the .tgz files
    items = [tar.extractfile(ii) for ii in items]
    # convert to pickle-able format
    items = [io.BytesIO(ii.read()) for ii in items]
    tar.close()
    return items

prepped = prep_data('../data/NLP/nyt_corpus_LDC2008T19.tgz')

xml_stack = Parallel(n_jobs=-1)(delayed(extract_xmls)(ii) for ii in tqdm(prepped))
xmls = [item for sublist in xml_stack for item in sublist]
# ----------------------------------------------------------------------------------------
# process the xml
# ----------------------------------------------------------------------------------------
xmls = Parallel(n_jobs=-1)(delayed(parse_xml)(ii) for ii in tqdm(xmls))
# get rid of the repeat on the body text
for xx in xmls:
    xx['Body'] = xx['Body'].replace(xx['LeadParagraph'], '').strip()

xml_df = pd.DataFrame(xmls)

del(prepped)
del(xml_stack)
del(xmls)

df_loc = xml_df[xml_df['Locations'] != 'NA']

xml_df.to_csv('../data/NLP/nyt_corpus.csv', index=False)