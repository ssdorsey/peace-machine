"""
File for holding general helper functions

@ ssdorsey
"""
import re
import os
import datetime
from dateutil import parser
import unicodedata
from urllib.parse import urlparse
import nltk
import pandas as pd
import spacy 
nlp = spacy.load('en_core_web_sm')

def strip_url(url):
    """
    strips a url of all the fluff
    """
    parsed = urlparse(url)
    sturl = parsed.netloc + parsed.path
    # strip www.
    sturl = sturl.replace('www.', '')
    return sturl


def cut_dateline(_string, thresh=30):
    """
    removes the dateline from the beginning of a news story
    :param text: string, generally the body of a news story that may have a 
                    dateline
    :param thresh: how far into the text to look for the dateline indicators
    :return: string with dateline cut out
    """
    if ' —' in _string[:thresh]:
        return _string[_string.index(' — ')+3:]
    elif '--' in _string[:thresh]:
        return _string[_string.index('--')+2:]
    elif ' -' in _string[:thresh]:
        return _string[_string.index(' - ')+3:]
    elif ': ' in _string[:thresh-10]:
        return _string[_string.index(': ')+2:]
    elif bool(re.search(r'(\(.*?\)\s)', _string[:thresh])):
        return re.sub(r'(\(.*?\))', '', _string)
    # if no dateline is found, return the same string
    return _string

def parse_date(date):
    """
    Parses the dates of the various sites
    :param date: string or datetime that needs standardizing
    :return: None for unparsed dates, datetime formatted dates otherwise
    """
    # if it's already a datetime, return the same
    if isinstance(date, datetime.datetime):
        return date
    # this is for the funky format often associated with Guardian articles
    try:
        if 'EDT' in date or 'EST' in date:
            date = unicodedata.normalize('NFKD', date)
            date = re.sub(r'( \d+\.\d+ (EST|EDT))', '', date)
            return parser.parse(date)
    except:
        # print(f'ERROR ON {date_string}')
        return

    # try to do a general parse and a few fixes if it doesn't work
    try:
        return parser.parse(date)
    except:
        if ' | ' in date:
            date = date.split(' | ')[0]
        if bool(re.search('\dT\d', date)): 
            date = date.split('T')[0]
        if '/ ' in date: 
            date = date.split('/ ')[0]
        if date.startswith('Associated Press'):
            return

    # try one more time with the fixes and if that doesn't do it just move on
    try:
        return parser.parse(date)
    except:
        # print(f'ERROR ON {date_string}')
        return


def mreplace(text, substitutions):
    """
    Replace multiple things in a string at once.
    :param text: string with pieces that need replacing
    :param substitutions: dict with from keys and to values
    :return: string with substitutions inserted
    """
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    result = regex.sub(lambda match: substitutions[match.group(0)], text)
    return result

# move file

# pull url from filename


def pull_url(path):
    """
    Pull the url from a file path.
    :param path: string filepath format
    :return: string of url extracted from filepath
    """
    # fix slash format
    new_path = path.replace('\\', '/')
    # split the path apart then go from the first folder with a '.'
    folders = new_path.split('/')
    first_period = [num for num, ff in enumerate(folders) if '.' in ff][0]
    new_path = '/'.join(folders[first_period:])
    # get rid of www etc
    if 'www.' in new_path:
        new_path = new_path.replace('www.', '')
    if new_path.endswith('index.html'):
        new_path = new_path.replace('index.html', '')
    if new_path.endswith('.html'):
        new_path = new_path.replace('.html', '')
    if new_path.endswith('/'):
        new_path = new_path[:-1]
    return new_path


def pull_domain(url):
    """
    Pull the domain (without www.) from a url
    :param: string in url format
    :return: string of only domain
    """
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def build_combined(doc):
    """
    combines titles and text of docs as they are available
    :param doc: dictionary from news-please output
    :return: string of combined text
    """
    try:
        if doc['title'] and doc['maintext']:
            doc['combined'] = doc['title'] + '. ' + nltk.sent_tokenize(doc['maintext'])[0] # TODO: multilingual tokenizer needed
            return doc
        if doc['title'] and doc['maintext']:
            doc['combined'] = doc['title'] + '. ' + doc['maintext'][:100]
            return doc
    except:
        pass

    try:
        if doc['title'] and doc['description']:
            doc['combined'] = doc['title'] + '. ' + nltk.sent_tokenize(doc['description'])[0]
            return doc
    except:
        pass
    
    if doc['title']:
        doc['combined'] = doc['title']
        return doc

    if doc['maintext']:
        doc['combined'] = doc['maintext']
        return doc

    try:
        if doc['description']:
            doc['combined'] = doc['description']
            return doc
    except:
        pass

    return doc


# import background info for placing events roughly
# TODO: create a local Nomin
demo = pd.read_csv('peacemachine/data/demonyms.csv')
demo = pd.Series(demo.location.values,index=demo.demonym).to_dict()
demonyms = list(demo.keys())
locations = set(demo.values())
city_country = pd.read_csv('peacemachine/data/world-cities.csv')
city_dict = pd.Series(city_country.country.values,index=city_country.city).to_dict()
cities = list(city_dict.keys())
countries = set([cc.lower() for cc in city_country['country']])


def is_country(name):
    """
    checks to see if a name matches a country, if it doesn't
    it pulls from 
    """
    # check to see if it's a country
    # fuzz_country = process.extract(name, countries, limit=1)[0]
    # if fuzz_country[1] > 90:
        # return(pycountry.countries.lookup(fuzz_country[0]).name)
    if name in countries:
        return(name.title())

    # # check to see if it's a city
    # fuzz_city = process.extract(name, cities, limit=1)[0]
    # # if it's a city, return the country name
    # if fuzz_city[1] > 90:
    if name in city_dict:
        country = city_dict[name]
        return(country.title())

    else:
        return(None)

def most_frequent(_list): 
    return max(set(_list), key = _list.count) 

def pull_country(sentences):
    """
    pulls any country mentions either from a string or list of strings
    TODO: roll this into the extractor where I already have a doc made
    TODO: work around the fuzzy string matching... it's pretty slow 
    """
    # check format
    if type(sentences) == str:
        sentences = [sentences]
    # Pull the GPE
    gpes = []
    try:
        for sentence in sentences:
            doc = nlp(sentence)
            for ent in doc.ents:

                # if it's a geopolitical entity just attach 
                if ent.label_ == 'GPE':
                    if ent.text in ['U.S.', 'US']:
                        gpes.append('united states')
                    else:    
                        gpes.append(ent.text.lower())
                # if it's a nationality look it up in the demonyms
                elif ent.label_ == 'NORP':
                    norp = ent.text.lower()
                    # fuzzy string match
                    # fuzz_m = process.extract(norp, demonyms, limit=1)[0]
                    # if fuzz_m[1] > 90:
                    #     gpes.append(demo[fuzz_m[0]])
                    if norp in demo:
                        gpes.append(norp)
                # sometimes spaCy mistakes countries for people so just make sure
                else:
                    # check for a full entity match 
                    # fuzz_m = process.extract(ent.text.lower(), locations, limit=1)[0]
                    # if fuzz_m[1] > 90:
                    #     gpes.append(fuzz_m[0])
                    #     continue
                    if ent.text.lower() in locations:
                        gpes.append(ent.text.lower())
                    # if there's no entity match, check inside the tokens
                    for tok in ent:
                        # fuzz_m = process.extract(tok.text.lower(), locations, limit=1)[0]
                        # if fuzz_m[1] > 90:
                        #     gpes.append(fuzz_m[0])
                        if tok.text.lower() in locations:
                            gpes.append(tok.text.lower())
    except:
        return None

    if len(gpes) == 0:
        return None
    elif len(gpes) == 1:
        return is_country(gpes[0])
    else:
        # TODO: use a smarter way to pick the location
        # return ([is_country(gg) for gg in gpes])
        return most_frequent([is_country(gg) for gg in gpes])

# insert the location for local sources that don't have one
available_countries = [fn.split('_')[1].split('.')[0] for fn in os.listdir('peacemachine/data/domains') 
    if fn.startswith('domains_') and not fn.endswith('international.txt')]

domain_locs = {}
for ac in available_countries:
    with open(f'peacemachine/data/domains/domains_{ac}.txt', 'r') as _file:
        domains = [dd.strip() for dd in _file.readlines()]
    for dd in domains:
        domain_locs[dd] = ac
        