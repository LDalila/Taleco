from collections import defaultdict
from nltk.tokenize import word_tokenize
from pprint import pprint
from scipy.optimize import curve_fit
from spacy.lang.en.stop_words import STOP_WORDS
from tqdm import tqdm
from sklearn.metrics import r2_score
import json
import math
import numpy as np
import os
import spacy
import string
import re

FILTER_TABLE_OF_CONTENTS = re.compile('\.{4,}')

cutoff = 25
cleaned_until = 1999
threshold = 5

def sigmoid(x, L, x0, k, b): # Spread, cutoff date, speed of change, val -inf
    return L / (1 + np.exp(-k*(x - x0))) + b

author = 'sunstein'
in_corpus = 'cermine'

if author == 'sunstein':
    skip = 1
    years = list(range(1987, 2006, skip))
else:
    skip = 1
    years = list(range(2004, 2015))

def preprocess(text):
    text = FILTER_TABLE_OF_CONTENTS.sub('...', text)
    return text

occurrences = defaultdict(lambda: [0]*len(years))
num_words = []

np.seterr(all='raise')

for year in tqdm(years):
    year_words = []
    num_year_words = 0
    text = ''
    if author == 'sunstein':
        for file in os.listdir('sunstein/processed/'):
            if any(file[:4] == str(y) for y in range(year, year + skip)) and \
                (file.endswith(f'_{in_corpus}.txt') and year > cleaned_until \
                or file.endswith('final.txt') and year <= cleaned_until):
                
                for word in word_tokenize(open('sunstein/processed/' + file).read()):
                        num_year_words += 1
                        lower = word.lower()
                        if lower not in STOP_WORDS and not all(char in string.punctuation for char in word):
                            occurrences[lower][year - years[0]] += 1
    else:
        with open('becker-posner.json') as f:
            data = json.load(f)
            for article in data:
                if article['date'][-4:] == str(year):
                    for word in word_tokenize(article['text']):
                        num_year_words += 1
                        lower = word.lower()
                        if lower not in STOP_WORDS and not all(char in string.punctuation for char in word):
                            occurrences[lower][year - years[0]] += 1
    num_words.append(num_year_words)

med_year = np.median(years)
myear = min(years)
Myear = max(years)

print(occurrences['government'])

with open(f'word_evolution_{cutoff}_{cleaned_until}.txt', 'w') as f:
    for word, occ in tqdm(occurrences.items()):
        if sum(occ) <= cutoff:
            continue
        try:
            occ = np.divide(occ, num_words)
            p0 = [max(occ), med_year, 1, min(occ)]
            popt, pcov = curve_fit(sigmoid, years, occ, p0, method='dogbox')

            y_pred = sigmoid(years, *popt)
            r2 = r2_score(occ, y_pred)
            if not myear + 1 < popt[1] < Myear - 1:
                continue
            val_inf = sigmoid(math.inf, *popt)
            val_minf = sigmoid(-math.inf, *popt)
            inf_ratio = val_inf/val_minf
            if abs(inf_ratio) < 1:
                inf_ratio = 1/inf_ratio
            # f(inf) = L + b, f(-inf) = b, f(inf)/f(-inf) = 1 + L/b
            # Skip if L > 0 and -2 < f(inf)/f(-inf) < 2 or L < 0 and -0.5 > f(inf)/f(-inf) > 0.5 -> occurrences counts changes by x%, -50% < x < +100%
            if abs(inf_ratio) < threshold:
                continue
            perr = np.sqrt(np.diag(pcov))
            print(('[' + word  + '] ').ljust(20) + ('×' if inf_ratio > 0 else '÷') + str(abs(round(inf_ratio, 2))) + ', params: ' + str(popt) + ', error: ' + str(perr) + ', cutoff: ' + str(round(popt[1], 1)))
            #print(popt, occ,)
            #print(f"{popt[0]} / (1 + exp(-{popt[2]}*(x - {popt[1]}))) + {popt[3]}")
            f.write(word + ' ' + str(popt) + ' ' + str(pcov) + ' ' + str(occ) + ' ' + str(r2)+ '\n')
        except (RuntimeError, FloatingPointError):
            pass

# T0D0
# https://stackoverflow.com/questions/51372724/how-to-speed-up-spacy-lemmatization
# https://stats.stackexchange.com/questions/362520/how-to-know-if-a-parameter-is-statistically-significant-in-a-curve-fit-estimat

