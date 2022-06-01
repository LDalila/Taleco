from pprint import pprint
from spacy.lang.en.stop_words import STOP_WORDS
from tqdm import tqdm

import json
import nltk
import os
import spacy
import string

# nltk.download('punkt')

# nlp = spacy.load("en_core_web_trf")

author = 'sunstein'
in_corpus = 'cermine'

cleaned_until = 1994

if author == 'sunstein':
    years = range(1987, 2006)
    out_file = open(f'results/{author}_{in_corpus}_basic_analysis.txt', 'w')
else:
    years = range(2004, 2015)
    out_file = open(f'results/{author}_basic_analysis.txt', 'w')

for year in tqdm(years):
    text = ''
    if author == 'sunstein':
        for file in os.listdir('sunstein/processed/'):
            if file[:4] == str(year) and \
                (file.endswith(f'_{in_corpus}.txt') and year > cleaned_until \
                or file.endswith('_mclean.txt') and year <= cleaned_until):
                
                text += open('sunstein/processed/' + file).read() + '\n\n'
    else:
        with open('becker-posner.json') as f:
            data = json.load(f)
            for article in data:
                if article['date'][-4:] == str(year):
                    text += article['text'] + '\n\n'
    # doc = nlp(text)
    
    # sentences = []
    # cur_sentence = []
    # for sent in doc.sents:
        # for token in sent:
            # if not token.text.lower() in STOP_WORDS and not token.is_punct:
                # cur_sentence.append(token.lemma_)
        # sentences.append(cur_sentence)
        # cur_sentence = []
    # print(sentences)
    # break
    
    text = text.replace('’', '\'')
    
    out_file.write(str(year))
    out_file.write('\n'*2)
    
    tokenized_text = nltk.word_tokenize(text)
    filtered_text = [token for token in tqdm(tokenized_text) if token.lower() not in STOP_WORDS and not all(char in string.punctuation for char in token)]
    filtered_lower_text = list(token.lower() if token.isupper() and not any(char in string.punctuation for char in token) else token for token in tqdm(filtered_text))

    unigrams = nltk.FreqDist(filtered_lower_text).most_common() # Unigrams
    bigrams = nltk.FreqDist(nltk.bigrams(filtered_lower_text)).most_common() # Bigrams
    trigrams = nltk.FreqDist(nltk.trigrams(filtered_lower_text)).most_common() # Trigrams
    
    for unigram, count in unigrams[:25]:
        if count < 50:
            break
        out_file.write(str((unigram, count)) + '\n')
    out_file.write('\n')
    
    for bigram, count in bigrams[:25]:
        if count < 25:
            break
        out_file.write(str((bigram, count)) + '\n')
    out_file.write('\n')
    
    for trigram, count in trigrams[:25]:
        if count < 10:
            break
        out_file.write(str((trigram, count)) + '\n')
    out_file.write('\n'*2)

out_file.close()
    