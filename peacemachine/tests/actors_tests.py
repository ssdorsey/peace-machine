import re
import spacy
import pandas as pd
from allennlp.predictors import Predictor
import allennlp_models.syntax.srl

from nltk import Tree

nlp = spacy.load('en_core_web_sm')

_srl = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.03.24.tar.gz",
                            cuda_device=0)

data = pd.read_csv('../data/actor_data_V2.csv')

# test_sentence = 'Sixteen men, arrested last month during a crackdown on homosexuality by the authorities in Egypt, have been sentenced to three years in prison.'
# test_sentence = 'Stocks jumped as investors rallied around efforts to reopen parts of the economy.'
test_sentence = 'German Chancellor Angela Merkel said on Wednesday that social distancing rules to contain the spread of the coronavirus would remain in place until at least May 3 but some shops could reopen next week.'


def pull_verb_dict(verb_set):
    """
    pulls the arguments from an SRL verb set

    :param verb_set: a single verb-set from the SRL model
    :return: dictionary with the SRL arguments as keys and a dict
             with text and index as keys
    """
    args = re.findall(r'\[(.*?)\]', verb_set['description'])
    args_d = {ii[:ii.index(':')]:ii[ii.index(':')+2:] for ii in args}
    # include the indices of the values
    for k in args_d.keys():
        index = [n for n, v in enumerate(verb_set['tags']) if v != 'O' and v[v.index('-')+1: ] == k]
        args_d[k] = {'text': args_d[k], 'index': index}
    return args_d


# -----------------------------------------------------------
# Spacy
# -----------------------------------------------------------
# TODO: get spacy features from the SRL (which already does this)

# getting the root
parsed = nlp(test_sentence)
parsed = parsed[0:len(parsed)]
root = parsed.root

# TODO: make sure the root isn't something like "say", "argue", "claim", or "estimate"
    # if it is, navigate down the tree:
        # for ch in root.children:
        #     if ch.pos_ == 'VERB':
        #         print( ch )

# -----------------------------------------------------------
# SRL
# -----------------------------------------------------------
# do the SRL
labelled = _srl.predict(test_sentence)

# pick the right verb set
# TODO: deal with multiple srl options, for now just using first 
srl_choice =  [vv for vv in labelled['verbs'] if vv['verb'] == str(root)][0]
srl_dict = pull_verb_dict(srl_choice)

# -----------------------------------------------------------
# NER pull for each ARG
# -----------------------------------------------------------
ner = {ent: {'label': ent.label_, 'dep': [tok.dep_ for tok in ent]} for ent in parsed.ents}

ner_ranges = [range(nn[0].i, nn[-1].i+1) for nn in ner.keys()]

arg_ner = {}
for arg, arg_info in srl_dict.items():
    # get range for argument
    arg_range = range(arg_info['index'][0], arg_info['index'][-1] + 1)
    # pull the named entities
    arg_ner[arg] = [{kk: vv} for kk, vv in ner.items() if kk[0].i in arg_range]

# TODO: pick from among the NER for each arg, ex: {'ARG0': [
#           {German: {'label': 'NORP', 'dep': ['amod']}},
#           {Angela Merkel: {'label': 'PERSON', 'dep': ['compound', 'nsubj']}}
#           ]}

# for ARG0 priority to dep: nsubj, then label: {PERSON}, then label: ORG


# -----------------------------------------------------------
# NER lookup
# -----------------------------------------------------------


# -----------------------------------------------------------
# noun chunk for each ARG
# -----------------------------------------------------------
def span_overlap(span, ranges):
    """
    Checks for overlap in a spacy spance and an iterable of ranges
    :param span: the span to check
    :param ranges: the iterable of ranges to check 
    :return: bool, true if span overlaps any range, otherwise false
    """
    span_range = range(span.start, span.end)
    for _range in ranges:
        if bool( set(span_range).intersection( _range ) ):
            return True
    return False

noun_chunks = {chunk: {'dep': [tok.dep_ for tok in chunk]} for chunk in parsed.noun_chunks}

arg_chunks = {}
for arg, arg_info in srl_dict.items():
    # get range for argument
    arg_range = range(arg_info['index'][0], arg_info['index'][-1] + 1)
    # pull the chunks for each argument
    chunks = [{kk: vv} for kk, vv in noun_chunks.items() if kk[0].i in arg_range]
    # take away chunks that are already in named entities
    chunks = [{kk:vv} for ch in chunks for kk, vv in ch.items() if not span_overlap(kk, ner_ranges)]
    # insert back into the dict
    arg_chunks[arg] = chunks

# -----------------------------------------------------------
# classify what I get
# -----------------------------------------------------------



# -----------------------------------------------------------
# junk
# -----------------------------------------------------------
doc = nlp(test_sentence)

for sent in doc.sents:
    doc = sent
    break

for nc in doc.noun_chunks:
    print(nc)

for ent in doc.ents:
    print(ent.text + ' | ' + ent.label_)

for chunk in doc.noun_chunks:
    print(chunk.text + ' | ' + chunk.root.text + ' | ' + chunk.root.dep_ + ' | ' +
            chunk.root.head.text)

for token in doc:
    print(token.text + ' | ' + token.dep_ + ' | ' + token.head.text + ' | ' + token.head.pos_ + ' | ',
            [child for child in token.children])

spacy.displacy.render(doc, style='dep', jupyter=True, options={'compact':True})

# Tree
def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_


[to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]

# Finding a verb with a subject from below — good
roles = {}
for possible_subject in doc:
    if possible_subject.dep_.startswith('nsubj') and possible_subject.head.pos_ == 'VERB':
        roles[possible_subject] = possible_subject.head
print(roles)


def unwrap_agent_aliases(df):
    """
    unwraps the aliases from the ICEWS agent dataframe
    :param df: the df from 
    """
    # pull out the aliases
    alias_frame = df['Aliases'].str.split(' \|\| ', expand=True)
    # put the type/sector back in
    alias_frame.loc[:, 'Agent Type'] = df['Agent Type']
    alias_frame.loc[:, 'Sectors'] = df['Sectors']
    # melt it 
    melted = alias_frame.melt(id_vars=['Agent Type', 'Sectors'])
    # rename the Agent Name
    melted = melted.rename({'value': 'Agent Name'}, axis=1)
    melted = melted.drop('variable', axis=1)
    # drop all the empty names (artifact from the expansion)
    melted = melted.dropna(subset=['Agent Name'])
    # drop the aliases from the original frame
    df = df.drop('Aliases', axis=1)
    # concat the aliases back in
    df_tall = pd.concat([df, melted])
    # split the Sectors
    df_tall.loc[:, 'Sectors'] = df_tall['Sectors'].str.split(' \|\| ')
    return df_tall
