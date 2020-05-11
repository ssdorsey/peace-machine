import re
import spacy
import pandas as pd
from allennlp.predictors import Predictor
import allennlp_models.syntax.srl

van = spacy.load('en_core_web_sm')
nlp = spacy.load('../data/actors/phoenix_ner')
_srl = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.03.24.tar.gz",
                            cuda_device=0)

# data = pd.read_csv('../data/actor_data_V2.csv')

sentence = "Five journalists were arrested by Kenyan police in a renewed crackdown on dissent"
sentence = "Journalists and academics were arrested by Kenyan police in a renewed crackdown on dissent"
sentence2 = 'German Chancellor Angela Merkel said on Wednesday that social distancing rules to contain the spread of the coronavirus would remain in place until at least May 3 but some shops could reopen next week.'
sentence3 = 'Tom Jones, a local reporter, was savagely beat by hooligans yesterday evening.'

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


class Actors:
    """
    main class for pull the actors out of a sentence
    best to pre-process SRL as that is done much more efficiently in batches
    """
    def __init__(self, sentence, srl_sentence=None):
        # set up data
        self.sentence = sentence
        self.srl_sentence = srl_sentence
        self.main()

    def main(self):
        """
        main function for pulling the actors from a sentence
        """
        # first see if I need to run the SRL
        if not self.srl_sentence:
            self.srl_sentence = _srl.predict(self.sentence)
        # convert to spaCy doc TODO: integrate custom pipeline into the SRL, which uses spaCy initally
        self.doc = nlp(self.sentence)
        self.root = self.get_root()
        # pick the right verb set
        srl_choice =  [vv for vv in self.srl_sentence['verbs'] if vv['verb'] == str(self.root)][0]
        self.srl_dict = pull_verb_dict(srl_choice)
        # pull out the entities
        self.raw_ents = [ent for ent in self.doc.ents]
        self.entities = self.get_entities()
        # lookup unidentified PERSON / ORG in Phoenix entity DB

        # lookup unidentified PERSON / ORG on Wiki

        # if one of my ARGS is still missing an entity / agent, include noun chunk or whole arg

    def get_root(self):
        """
        pulls the root out of a spaCy doc
        :param doc: spaCy document, should be single sentence
        :return: token - root of the sentence
        """
        # getting the root
        span = self.doc[0:len(self.doc)]
        root = span.root
        # if the root is something like "say", "claim", or "estimate", 
            # move to a VERB child (if available)
        speech_lemmas = {'say', 'claim', 'estimate', 'announce', 'report'} # TODO: expand this list
        if root.lemma_ in speech_lemmas:
            for ch in root.children:
                if ch.pos_ == 'VERB':
                    root = ch
                    break
        return root

    def get_entities(self):
        """
        pulls the entities out of a spaCy document and puts them + 
            their associated features in a dict
        """
        # here's all the entities
        self.all_entities = {ent: {'label': ent.label_, 'id': ent.ent_id_, 'dep': [tok.dep_ for tok in ent]} for
                             ent in self.raw_ents}
        # here's all the AGENTS
        self.
        # restricted to entity types we'll use https://spacy.io/api/annotation#named-entities
        ner_res = {ent: {'label': ent.label_, 'id': ent.ent_id_, 'dep': [tok.dep_ for tok in ent]} for 
                    ent in self.doc.ents if ent.label_ in 
                    {'PERSON', 'AGENT', 'ORG', 'GPE', 'EVENT', 'LAW', 'FAC', 'PRODUCT'}} 

        # ner_ranges = [range(nn[0].i, nn[-1].i+1) for nn in ner_res.keys()]

        arg_ner = {}
        for arg, arg_info in self.srl_dict.items():
            # get range for argument
            arg_range = range(arg_info['index'][0], arg_info['index'][-1] + 1)
            # pull the named entities
            arg_ner[arg] = [{kk: vv} for kk, vv in ner_res.items() if kk[0].i in arg_range]
        return arg_ner

    def get_appos(ent):
        """
        checks for appos of a span/token and returns if available
        """
        if isinstance(ent, spacy.tokens.span.Span):
            ent = ent[-1]
        # check for appos children
        appos = [ch for ch in ent.children if ch.dep_ == 'appos'][0]
        


# -----------------------------------------------------------
# Classify 
# -----------------------------------------------------------

# -------------------------
# Lookup in ICEWS actors/agents
# -------------------------
# actors = unwrap_aliases(pd.read_csv('../data/actors/icews.actors.20181119.csv'))
# actors = pd.read_csv('../data/actors/icews.actors.20181119.csv')


"""
pseudo-code for entitiy classification

if entity['label'] == 'AGENT':
    look it up in a dictionary from the ICEWS agents list (fuzzy string match?)

if entity['label'] == 'PERSON':
    check in the ICEWS actors
"""

# -------------------------
# Lookup descriptors 
# -------------------------


# -------------------------
# Lookup leftover online
# -------------------------


# def unwrap_aliases(df):
    
