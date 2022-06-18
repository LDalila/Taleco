from pprint import pprint

import json
import os
import re

FILTER_TABLE_OF_CONTENTS = re.compile('\.{4,}')

from pprint import pprint
from tqdm import tqdm

author = 'sunstein'
in_corpus = 'final'

cleaned_until = 2000

if author == 'sunstein':
    skip = 1
    years = list(range(1987, 2006, skip))
else:
    skip = 1
    years = list(range(2004, 2015))

def preprocess(text):
    text = FILTER_TABLE_OF_CONTENTS.sub('...', text)
    return text

token_list = ['democratic', 'democracy', 'democrat', 'allocation', 'distribution', 'resources', 'unjust', 'unjust background', 'poverty', 'poor', 'rich', 'discrimination', 'ideology', 'class', 'deprivation', 'deprived', 'domination', 'dominated', 'oppression', 'oppressed', 'dissonance', 'autonomy', 'autonomous', 'non-autonomous', 'nonautonomous', 'freedom', 'liberty', 'liberalism', 'libertarian', 'virtue', 'civic', 'republican', 'republicanism', 'paternalism', 'republic', 'government', 'citizenship', 'deliberation', 'deliberate', 'discussion', 'bias', 'biases', 'heuristics', 'market', 'capability', 'capabilities', 'behavioral', 'behavioral economics', 'cognitive', 'prospect theory', 'self-control', 'kahneman', 'tversky', 'opportunity', 'opportunities', 'homo economicus', 'preferences', 'wealth', 'availability', 'willingness', 'endogenous', 'rationality', 'rational', 'status quo', 'information', 'self', 'selves']

res_rel = []
res_abs = []

for year in tqdm(years):
    text = ''
    if author == 'sunstein':
        for file in os.listdir('sunstein/processed/'):
            if file.startswith(str(year)):
                if (file.endswith(f'_{in_corpus}.txt') and year <= cleaned_until) \
                    or (file.endswith('_cermine.txt') and year > cleaned_until):
                    text += preprocess(open('sunstein/processed/' + file).read())
    else:
        with open('becker-posner.json') as f:
            data = json.load(f)
            for article in data:
                if article['date'][-4:] == str(year):
                    text += article['text']
    rel_occ = []
    abs_occ = []
    for token in token_list:
        occurrences = text.lower().count(token)
        abs_occ.append(occurrences)
        rel_occ.append(occurrences/len(text) if len(text) else 0)
    res_rel.append(rel_occ)
    res_abs.append(abs_occ)

print(', '.join(token_list))

for year, res in zip(years, res_rel):
    print(year, ', ', ', '.join(str(el) for el in res))

print()

for year, res in zip(years, res_abs):
    print(year, ', ', ', '.join(str(el) for el in res))
