import pandas as pd
import spacy
from spacy.pipeline import EntityRuler
import inflect

p = inflect.engine()

# setup spaCy
nlp = spacy.load("en_core_web_sm")
ruler = EntityRuler(nlp)

# Import the data 
actors = pd.read_csv('../data/actors/icews.actors.20181119.csv')
agents = pd.read_csv('../data/actors/icews.agents.20140112.csv')

# -------------------------------------------------------------
# Agents
# -------------------------------------------------------------
# convert label
agents.loc[:, 'Agent Type'] = agents['Agent Type'].replace(
    {'Individual': 'AGENT',
    'Group': 'ORG'}
)

agents.loc[: , 'Agent Name'] = agents['Agent Name'].str.replace('Minist', 'Ministry')
agents.loc[: , 'Aliases'] = agents['Aliases'].str.replace('Minist', 'Ministry')


def pattern_from_row(row):
    """
    creates a spaCy rules-matched pattern from an ICEWS row
    """
    # the first name
    a_name = row['Agent Name'].lower()
    # the aliases
    aliases = [al.lower() for al in row['Aliases'].split(r' || ')]
    all_names = [a_name] + aliases
    # format in a way spaCy likes
    pat = []
    for name in all_names:
        label = row['Agent Type']
        # deal with plurals for individuals
        if label == 'PERSON':
            pat.append({'label': label, 
                'pattern':[{'LOWER': p.plural(segment)} for segment in name.split()]})
        # then singular for everybody
        pat.append({'label': label, 
            'pattern':[{'LOWER': segment} for segment in name.split()]})
    return pat


agent_patterns = []
for row_num in range(agents.shape[0]):
    agent_patterns += pattern_from_row(agents.iloc[row_num])

# add the agents to the Matcher
ruler.add_patterns(agent_patterns)

# add to pipeline
nlp.add_pipe(ruler)

# save model
nlp.to_disk('../data/actors/icews_ner')


