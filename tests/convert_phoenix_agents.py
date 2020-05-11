import re
import spacy
from spacy.pipeline import EntityRuler
import inflect

p = inflect.engine()

nlp = spacy.load("en_core_web_sm")
ruler = EntityRuler(nlp)

data_prefix = '../data/actors/'

ethnic = 'CAMEO.EthnicGroups.actors.txt'
religious = 'CAMEO.ReligiousGroups.actors.txt'
country_actors = 'Phoenix.Countries.actors.txt'
international_actors = 'Phoenix.International.actors.txt'

# start with agents
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

# add the agents to the Matcher
ruler.add_patterns(agent_patterns)

# add to pipeline
nlp.add_pipe(ruler)

# save model
nlp.to_disk('../data/actors/phoenix_ner')

