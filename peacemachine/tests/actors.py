import re
import spacy
import pandas as pd
from allennlp.predictors import Predictor
import allennlp_models.structured_prediction.predictors.srl
# import allennlp_models.syntax.srl

nlp = spacy.load('data/actors/phoenix_ner')
_srl = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.03.24.tar.gz",
                            cuda_device=0)

# data = pd.read_csv('../data/actor_data_V2.csv')

sentence = "Journalists and academics were arrested by Kenyan police in a renewed crackdown on dissent."
sentence2 = 'German Chancellor Angela Merkel said on Wednesday that social distancing rules to contain the spread of the coronavirus would remain in place until at least May 3 but some shops could reopen next week.'
sentence3 = 'Tom Jones, a local reporter, was savagely beat by hooligans yesterday evening.'
sentence4 = 'Ban-Ki Moon, the U.N. Secretary General, has announced that he will step down at the end of this year.'


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
        # TODO: lookup unidentified PERSON / ORG on Wiki

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
        # speech_lemmas = {'say', 'claim', 'estimate', 'announce', 'report'} # TODO: expand this list
        # if root.lemma_ in speech_lemmas:
        #     for ch in root.children:
        #         if ch.pos_ == 'VERB':
        #             root = ch
        #             break
        return root


    def get_entities(self):
        """
        pulls the entities out of a spaCy document and puts them + 
            their associated features in a dict
        """
        # isolate ID'd ents
        self.id_ents = [ent for ent in self.raw_ents if ent.ent_id_]
        self.id_ents_index = [tok.i for span in self.id_ents for tok in span]
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

        # attach any appos/compound for PERSON TODO: clean up these loops... 
        for k, v in arg_ner.items():
            for entity_dict in v:
                for vk, vv in entity_dict.items():
                    if 'label' not in vv:
                        continue
                    if vv['label']=='PERSON':
                        desc = self.get_descriptive(vk)
                        if desc['descriptors']:
                            vv['descriptors'] = desc['descriptors']
                        if desc['ids'] and not vv['id']: 
                            vv['id'] = desc['ids'][0]

        return arg_ner

    def get_descriptive(self, entity):
        """
        checks for appos and compounds of a span/token and returns if available
        :param ent: the span/token (entity) to check
        :return:
        """
        res = {'descriptors': [], 'ids': []}

        if isinstance(entity, spacy.tokens.span.Span):
            ent_index = [tok.i for tok in entity]
            sub_ent = entity[-1]
        else:
            sub_ent = entity
            ent_index = [entity.i]

        # check for appos
        appos = [ch for ch in sub_ent.children if ch.dep_ == 'appos']
        if len(appos) > 0:
            appos = appos[0]
            # check for appos chunk
            for nc in self.doc.noun_chunks:
                if appos in nc:
                    appos = nc
                    break
            # check if in ID's entities
            app = ' '.join([tok.text for tok in appos if tok not in entity])
            app_ids = [e.ent_id_ for e in appos.ents if e.ent_id_]
            # attach to results
            res['descriptors'].append(app)
            res['ids'] += app_ids

        # check for compound
        compound = [ch for ch in sub_ent.children if ch.dep_ == 'compound']
        if len(compound) > 0:
            compound = compound[0]
            for nc in self.doc.noun_chunks:
                if compound in nc:
                    compound = nc
                    break
            # check if in ID's entities
            comp = ' '.join([tok.text for tok in compound if tok not in entity])
            comp_ids = [e.ent_id_ for e in compound.ents if e.ent_id_]
            # attach to results
            res['descriptors'].append(comp)
            res['ids'] += comp_ids

        return(res)

def print_entities(ent_dict):
    for arg, ents in ent_dict.items():
        if arg=='V':
            continue
        print(arg)
        for ent in ents:
            print('\t' + list(ent.keys())[0].text +': '+ list(ent.values())[0]['id'])

print_entities(test.entities)
