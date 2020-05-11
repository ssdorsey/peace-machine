import re
import spacy
from spacy.pipeline import EntityRuler
import inflect

p = inflect.engine()

nlp = spacy.load("en_core_web_sm")
ruler = EntityRuler(nlp)

actor_re = re.compile(r'(.+?)\s?\[(.+)\]')

data_prefix = '../data/actors/'

# start with actors
with open(data_prefix+'Phoenix.Countries.actors.txt', 'r', encoding='utf8') as _file:
    countries = [line.strip() for line in _file.readlines()]

with open(data_prefix+'Phoenix.International.actors.txt', 'r', encoding='utf8') as _file:
    internationals = [line.strip() for line in _file.readlines()]

actors = countries + internationals
# get rid of the comments
actors = [line for line in actors if not line.startswith('#')]
# get rid of empty lines
actors = [line for line in actors if len(line) > 0]
# add tag for all the alternate name lines
for ii in range(len(actors)):
    line = actors[ii]
    print(line)
    if line.startswith('+'):
        prev_line = ii -1
        while True:
            if not actors[prev_line].startswith('+'):
                tag = actor_re.search(actors[prev_line]).groups()[1]
                actors[ii] = f'{line[1:]} [{tag}]'
                break
            prev_line -= 1


# convert to dict
agent_re = re.compile(r'(.+?)\s?\[(.+)\]')
agent_dict = {}
for line in actors:
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
        kplural = p.plural(k)
        if kplural not in agent_dict:
            pattern = [{'LOWER': segment} for segment in kplural.split()]

    agent_patterns.append({'label': 'AGENT', 'id': v,
        'pattern': pattern})



# TODO: convert codes to regex:
for ii in range(len(actors))
    # !person! = (man|men|woman|women|person)
    # !minist! = (minister|ministers|ministry|ministries)

# TODO: check for plurals



{'label': label, 'id': _id, 'pattern': [{'LOWER': }]}
