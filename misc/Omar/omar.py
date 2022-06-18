#pip install spacy
#python -m spacy download en_core_web_sm
#copy en_core_web_sm from C:\Users\rajiv_kale\AppData\Local\Continuum\Anaconda3\Lib\site-packages
#to C:\Users\rajiv_kale\AppData\Local\Continuum\Anaconda3\Anaconda3\Lib\site-packages\spacy\data\

#=============
# On AWS EC2 we did this.
# Login as ec2-user
#pip install spacy
# python -m spacy download en_core_web_sm
# cd /home/ec2-user/anaconda3/envs/tensorflow_p36/lib/python3.6/site-packages/
# cp -R en_core_web_sm   spacy/data/
print("TEST")
import spacy
spacy.load('en_core_web_sm')  # needs some installation and tweaking
from spacy.lang.en import English
parser = English()
def tokenize(text):
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens
print("TEST")

import nltk
#nltk.download('wordnet')
from nltk.corpus import wordnet as wn
def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma
    
from nltk.stem.wordnet import WordNetLemmatizer
def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)

print("TEST")

en_stop = set(nltk.corpus.stopwords.words('english'))

def prepare_text_for_lda(text):
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 4]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [get_lemma(token) for token in tokens]
    return tokens
print("TEST")

num_lines=0
with open('1988_Sunstein.txt') as f:
    for line in f:
        num_lines=num_lines+1
        if num_lines<10:
            print(line)
print("total number of lines=", num_lines)
print("TEST")


#random.random(): Returns the next random floating point number in the range [0.0, 1.0].
#We choose subset of the data
import random
text_data = []
with open('1988_Sunstein.txt') as f:
    for line in f:
        tokens = prepare_text_for_lda(line)
        if random.random() > .79:
            #print(tokens)
            text_data.append(tokens)
from gensim import corpora
dictionary = corpora.Dictionary(text_data)
corpus = [dictionary.doc2bow(text) for text in text_data]
dictionary[0]
len(dictionary)  # total tokens
corpus
# save corpus and dictionary to disk so that we can use it later during visualization
##import pickle
##pickle.dump(corpus, open('corpus.pkl', 'wb'))
##dictionary.save('dictionary.gensim')
import gensim
NUM_TOPICS = 5
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = NUM_TOPICS, id2word=dictionary, passes=15)
ldamodel.save('model5.gensim')
topics = ldamodel.print_topics(num_words=25)
with open("resultat TEST.txt","w") as f:
    for topic in topics:
        f.write(str(topic))