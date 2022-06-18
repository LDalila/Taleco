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
in_corpus = 'final'

cleaned_until = 2000

if author == 'sunstein':
    skip = 1
    years = list(range(1987, 2006, skip))
    out_file = open(f'results/{author}_{in_corpus}_{skip}_tfidf.txt', 'w')
else:
    skip = 1
    years = list(range(2004, 2015))
    out_file = open(f'results/posner-becker_{skip}_tfidf.txt', 'w')

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
            
        if (file.endswith(f'_{in_corpus}.txt') and year <= cleaned_until) \
            or (file.endswith('_cermine.txt') and year > cleaned_until):
            
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

for year in years:
    year_sents = []
    text = ''
    if author == 'sunstein':
        for file in tqdm(os.listdir('sunstein/processed/')):
            if any(file[:4] == str(y) for y in range(year, year + skip)) and \
                (file.endswith(f'_{in_corpus}.txt') and year > cleaned_until \
                or file.endswith('_mclean.txt') and year <= cleaned_until):

                year_sents.extend(tokenizer.tokenize(open('sunstein/processed/' + file).read()))
    else:
        with open('becker-posner.json') as f:
            data = json.load(f)
            for article in tqdm(data):
                if article['date'][-4:] == str(year):
                    year_sents.extend(tokenizer.tokenize(article['text']))
    
    doc_term_matrix = dictionary.doc2bow(year_sents)
    sentences_tfidf = tfidf[doc_term_matrix]
    d = {tokenizer.convert_tokens_to_string(dictionary.get(id)): value for id, value in sentences_tfidf}
    out_file.write(str(year) + '-' + str(year + skip - 1) + '\n')
    out = sorted(d.items(), key=lambda x:x[1], reverse=True)[:25]
    for i, (word, value) in enumerate(out):
        out_file.write(str(i).ljust(5) + word.ljust(25) + str(value) + '\n')
    out_file.write('\n')

out_file.close()
