from spacy.lang.en.stop_words import STOP_WORDS
from pprint import pprint

import json
import nltk
import os
import spacy
import string
import re

FILTER_TABLE_OF_CONTENTS = re.compile('\.{4,}')

from gensim import corpora
from gensim import models
from pprint import pprint
from tqdm import tqdm
from transformers import RobertaTokenizerFast

# nltk.download('punkt')
tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")

author = 'sunstein'
in_corpus = 'cermine'

cleaned_until = 1994

if author == 'sunstein':
    skip = 1
    years = list(range(1987, 2006, skip))
else:
    skip = 1
    years = list(range(2004, 2015))

def preprocess(text):
    text = FILTER_TABLE_OF_CONTENTS.sub('...', text)
    return text

print('Reading text')
words = []
full_text = ''
if author == 'sunstein':
    for file in tqdm(os.listdir('sunstein/processed/')):
        try:
            year = int(file[:4])
        except:
            continue
            
        if (file.endswith(f'_{in_corpus}.txt') and year > cleaned_until) \
            or (file.endswith('_mclean.txt') and year <= cleaned_until):
            
            in_text = open('sunstein/processed/' + file).read()
            in_text = preprocess(in_text)
            words.append(tokenizer.tokenize(in_text))
else:
    with open('becker-posner.json') as f:
        data = json.load(f)
        for article in tqdm(data):
            words.append(tokenizer.tokenize(article['text']))

# Convert sentences to bags of words
print('Creating dictionary')
dictionary = corpora.Dictionary(words)
print('Converting to bag of words')
bow = [dictionary.doc2bow(doc) for doc in words]
print('Creating TF-IDF')
tfidf = models.TfidfModel(bow)

token_list = ['Ġpaternal', 'Ġbehavioral', 'Ġrepublican', 'Ġbias', 'Ġbiases', 'istics']

print(token_list)
res_rel = []
res_abs = []

for year in tqdm(years):
    year_sents = []
    text = ''
    if author == 'sunstein':
        for file in os.listdir('sunstein/processed/'):
            if any(file[:4] == str(y) for y in range(year, year + skip)) and \
                (file.endswith(f'_{in_corpus}.txt') and year > cleaned_until \
                or file.endswith('_mclean.txt') and year <= cleaned_until):
                
                year_sents.extend(tokenizer.tokenize(open('sunstein/processed/' + file).read()))
    else:
        with open('becker-posner.json') as f:
            data = json.load(f)
            for article in data:
                if article['date'][-4:] == str(year):
                    year_sents.extend(tokenizer.tokenize(article['text']))
    rel_occ = []
    abs_occ = []
    doc_term_matrix = dictionary.doc2bow(year_sents)
    for token in token_list:
        occurrences = [v for k, v in doc_term_matrix if k == dictionary.token2id[token]]
        abs_occ.append(occurrences[0] if occurrences else 0)
        rel_occ.append(abs_occ[-1]/sum(len(x) for x in year_sents))
    res_rel.append(rel_occ)
    res_abs.append(abs_occ)

for year, res in zip(years, res_rel):
    print(year, ' '.join(str(el) for el in res))

print()

for year, res in zip(years, res_abs):
    print(year, ' '.join(str(el) for el in res))
