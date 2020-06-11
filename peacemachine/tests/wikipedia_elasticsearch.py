"""
Some sample queries of wikipedia on local elasticsearch
"""
import ast
from elasticsearch import Elasticsearch
import mwparserfromhell
import spacy
import re

nlp = spacy.load('../data/actors/phoenix_ner')
es =  Elasticsearch(['http://devlab-server:9200'])#,  ca_certs=False, verify_certs=False)

res = es.search(index="enwiki", body={"query": {"match_all": {}}})
print("Got %d Hits:" % res['hits']['total']['value'])
for hit in res['hits']['hits']:
    print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])

am = es.search(
    index="enwiki",
    body= {
        "query": {
            "match": {
                "title": {
                    "query": "Angela Merkel",
                    "fuzziness": "3"
                }
            }
        }
    }
)

print("Got %d Hits:" % am['hits']['total']['value'])
section_titles = ast.literal_eval(am['hits']['hits'][0]['_source']['section_titles'])
section_texts = ast.literal_eval(am['hits']['hits'][0]['_source']['section_texts'])

sections = dict(zip(section_titles, section_texts))
sections['Introduction']

aa = es.search(
    index="enwiki",
    body={
        "query":{
            "match_phrase":{
                "title": {
                    "query": "Abdulkareeem Ahmed",
                    # "auto_generate_synonyms_phrase_query": "false",
                    # "fuzziness": "AUTO",
                }
            }
        }
    }
)

print("Got %d Hits:" % aa['hits']['total']['value'])

# --------------------------
# code for known individual
# --------------------------
# get the intro paragraph
parsed_intro = mwparserfromhell.parse(sections['Introduction'])
intro_para = parsed_intro.strip_code().strip().split('\n')[0]
# get rid of everything between parentheses 
intro_para = re.sub(r'\(([^\)]+)\)', '', intro_para)
# convert to spacy
doc = nlp(intro_para)
first_sent = [sent for sent in doc.sents][0]
# get the entities
ents = [(ent, ent.label_, ent.ent_id_) for ent in first_sent.ents]
agents = [tup for tup in ents if tup[1] == 'AGENT']
# agent tags
tags = [agent[2] for agent in agents]


# --------------------------
# formalize 
# --------------------------

# class WikiAgent:


def wiki_search(name):
    """
    functions to search a local elasticsearch instance for names, returns the top result
    :param name: str name of the person to search in en-wiki (ex: 'Angela Merkel')
    :return: dictionary of the en-wiki match (if any)
    """
    res = es.search(
            index="enwiki",
            body= {
                "query": {
                    "match": {
                        "title": {
                            "query": name,
                            "fuzziness": "AUTO"
                        }
                    }
                }
            }
        )
    if len(res['hits']['hits']) > 0:
        return res['hits']['hits'][0]
    else:
        return None


def pull_intro(es_result):
    """
    """
    # get the intro paragraph
    section_titles = ast.literal_eval(es_result['_source']['section_titles'])
    section_texts = ast.literal_eval(es_result['_source']['section_texts'])
    sections = dict(zip(section_titles, section_texts))
    sections['Introduction']
    parsed_intro = mwparserfromhell.parse(sections['Introduction'])
    intro_para = parsed_intro.strip_code().strip().split('\n')[0]
    # get rid of everything between parentheses 
    intro_para = re.sub(r'\(([^\)]+)\)', '', intro_para)
    return intro_para


def pull_agents(text):
    """
    function to pull agents from a piece of text. currently only looks in the first sentence
    :param es_result: the result from wiki_search
    :return: list of the agents in the first sentence
    """
    # convert to spacy
    doc = nlp(text)
    first_sent = [sent for sent in doc.sents][0]
    # get the entities
    ents = [(ent, ent.label_, ent.ent_id_) for ent in first_sent.ents]
    agents = [tup for tup in ents if tup[1] == 'AGENT']
    # agent tags
    tags = [agent[2] for agent in agents]
    return tags


def name_tags(name):
    """
    takes in a name, searches en-wiki, returns tags
    :param name: name to search for in en-wiki
    :return: the tags associated with that name
    """
    es_result = wiki_search(name)
    intro_para = pull_intro(es_result)
    tags = pull_agents(intro_para)
    return tags
