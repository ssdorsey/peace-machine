"""
There are lot of problems with using the Countries actors.
     Most of all that it will be constantly out-of-date
     Maybe try to figure out what to do there...
"""

import re
import spacy
from spacy.pipeline import EntityRuler
import inflect

p = inflect.engine()

nlp = spacy.load("en_core_web_sm")
ruler = EntityRuler(nlp)


data_prefix = '../data/actors/'

# -------------------------------------------------------------------------------------
# Agents
# -------------------------------------------------------------------------------------
with open(data_prefix+'Phoenix.agents.txt', 'r', encoding='utf8') as _file:
    agents = [line.strip() for line in _file.readlines()]

# get rid of the comments
agents = [line for line in agents if not line.startswith('#')]
# get rid of empty lines
agents = [line for line in agents if len(line) > 0]
# skip first two lines which are guiding info
agents = agents[2:]
# remove {}
agents = [ag.replace('{}', '') for ag in agents]
# convert to dict
agent_re = re.compile(r'(.+?)\s?\[(.+)\]')
agent_dict = {}
for line in agents:
    reg = agent_re.search(line)
    agent = reg.groups()[0]
    code = reg.groups()[1]
    agent_dict[agent] = code
# lower
agent_dict = {k.lower(): v for k, v in agent_dict.items()}
# remove "_"
agent_dict = {k.replace('_', ' '): v for k, v in agent_dict.items()}
# build the patterns
agent_patterns = []
for k, v in agent_dict.items():
    if '!minist!' in k:
        ks = k.split()
        pattern = []
        for ii in ks:
            if '!minist!' in ii:
                pattern.append({'LOWER': {'REGEX': '^'+ii.replace('!minist!', '(minister|ministers|ministry|ministries)')+'$'}})
            else:
                pattern.append({'LOWER': ii})

    elif '!person!' in k:
        ks = k.split()
        pattern = []
        for ii in ks:
            if '!person!' in ii:
                pattern.append({'LOWER': {'REGEX': '^'+ii.replace('!person!', '(man|men|woman|women|person)')+'$'}})
            else:
                pattern.append({'LOWER': ii})

    else:
        pattern = [{'LOWER': segment} for segment in k.split()]
        # deal with the plurals
        kplural = p.plural(k)
        # if the plural form is not already in the dict, add it in
        if kplural not in agent_dict:
            plural_pattern = [{'LOWER': segment} for segment in kplural.split()]
            agent_patterns.append({'label': 'AGENT', 'id': v,
                'pattern': plural_pattern})
        # if the plural form is already in, do the standard pattern
    agent_patterns.append({'label': 'AGENT', 'id': v,
        'pattern': pattern})


# -------------------------------------------------------------------------------------
# Actors (international)
# -------------------------------------------------------------------------------------

with open(data_prefix+'Phoenix.International.actors.txt', 'r', encoding='utf8') as _file:
    internationals = [line.strip() for line in _file.readlines()]

actors = internationals
# get rid of the comments
actors = [line for line in actors if not line.startswith('#')]
# get rid of empty lines
actors = [line for line in actors if len(line) > 0]
# get rid of empty space
actors = [line.strip() for line in actors]
# get rid of the NGO and IGO leaders
actors = [line for line in actors if not 'NGO_Actors' in line]
actors = [line for line in actors if not 'IGOrulers.txt' in line]
# get rid of the businesses
actors = [line for line in actors if not '$' in line]

# convert to dict
actors_dict = {}
for ii in range(len(actors)):
    line = actors[ii]
    # if it's meta, pass
    if (line.startswith('+') or line.startswith(r'[')):
        continue
    # if it's a new actor, use
    k = line
    aliases = []
    tags = []
    jj = ii + 1
    # go through the following lines until we run out
    while True:
        if jj > len(actors)-1:
            break
        if actors[jj].startswith('+'):
            aliases.append(actors[jj][1:])
        elif actors[jj].startswith(r'['):
            tag = re.search(r'\[(.+)\]', actors[jj]).groups()[0]
            tags.append(tag)
        else:
            break
        jj += 1
    # insert into dict
    if len(tags) > 0:
        tag = tags[0]
    else:
        tag = None
    actors_dict[k] = {'aliases': aliases, 'id': tag}

# eliminate actors without tags
actors_dict = {k:v for k,v in actors_dict.items() if v['id']}
# for now, eliminate people, stick with institutions/positions
# anybody with a number in their ID is a person
actors_dict = {k: v for k, v in actors_dict.items() if not bool(re.search(r'(\d+)', v['id']))}


# build the patterns
actor_patterns = []
for k, v in actors_dict.items():
    # lower and remove '_'
    name = k.lower().replace('_', ' ')
    pattern = [{'LOWER': segment} for segment in name.split()]
    actor_patterns.append({'label': 'ORG', 'id': v['id'],
        'pattern': pattern})
    for alias in v['aliases']:
        name = alias.lower().replace('_', ' ')
        pattern = [{'LOWER': segment} for segment in name.split()]
        actor_patterns.append({'label': 'ORG', 'id': v['id'],
            'pattern': pattern})

# -------------------------------------------------------------------------------------------
# create spaCy model
# -------------------------------------------------------------------------------------------
# add the agents to the Matcher
ruler.add_patterns(agent_patterns)
ruler.add_patterns(actor_patterns)

# add to pipeline
nlp.add_pipe(ruler)

# save model
nlp.to_disk(data_prefix+'phoenix_ner')
