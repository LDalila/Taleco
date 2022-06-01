from spacy.lang.en.stop_words import STOP_WORDS
from pprint import pprint

import json
import nltk
import os
import spacy
import string

from gensim import corpora
from gensim import models
from tqdm import tqdm

# nltk.download('punkt')

nlp = spacy.load("en_core_web_trf")
nlp.max_length = 16000000

author = 'sunstein'
in_corpus = 'lapdf'

if author == 'sunstein':
    years = list(range(1987, 2006))
    out_file = open(f'results/{author}_{in_corpus}_basic_analysis.txt', 'w')
else:
    years = list(range(2004, 2015))
    out_file = open(f'results/{author}_basic_analysis.txt', 'w')

print('Reading text')
sents = []
full_text = ''
if author == 'sunstein':
    for file in tqdm(os.listdir('sunstein/processed/')):
        if file.endswith(f'_{in_corpus}.txt'):
            sents.extend(nlp(open('sunstein/processed/' + file).read()).sents)
else:
    with open('becker-posner.json') as f:
        data = json.load(f)
        for article in tqdm(data):
            sents.extend(nlp(article['text']).sents)
print('Lemmatizing')
full_sentences = []
cur_sentence = []
for sent in sents:
    for token in tqdm(sent):
        if not token.text.lower() in STOP_WORDS and not token.is_punct:
            cur_sentence.append(token.lemma_)
    full_sentences.append(cur_sentence)
    cur_sentence = []

# Convert sentences to bags of words
print('Creating dictionary')
full_dict = corpora.Dictionary(full_sentences)
print('Converting to bag of words')
full_dtm = [full_dict.doc2bow(doc) for doc in full_sentences]
print('Creating TF-IDF')
tfidf = models.TfidfModel(full_dtm)
print('Saving model')
tfidf.save('tfidf.bin')
print('Done')
input()


for year in years:
    year_sents = []
    text = ''
    if author == 'sunstein':
        for file in tqdm(os.listdir('sunstein/processed/')):
            if file[:4] == str(year) and file.endswith(f'_{in_corpus}.txt'):
                year_sents.extend(nlp(open('sunstein/processed/' + file).read()).sents)
    else:
        with open('becker-posner.json') as f:
            data = json.load(f)
            for article in tqdm(data):
                if article['date'][-4:] == str(year):
                    year_sents.extend(nlp(article['text']).sents)
    
    print(year)
    out_file.write(str(year))
    out_file.write('\n'*2)
    
    sentences = []
    cur_sentence = []
    for sent in tqdm(year_sents):
        for token in sent:
            if not token.text.lower() in STOP_WORDS and not token.is_punct:
                cur_sentence.append(token.lemma_)
        sentences.append(cur_sentence)
        cur_sentence = []
    
    # Convert sentences to bags of words
    dictionary = corpora.Dictionary(sentences)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in sentences]

    sentences_tfidf = tfidf[doc_term_matrix]
    d = {dictionary.get(id): value for doc in sentences_tfidf for id, value in doc}
    print(sorted(d.items(), key=lambda x:x[1], reverse=True)[:25])
    input()

out_file.close()
    