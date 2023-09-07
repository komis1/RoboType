### Utility functions to read phrases from various corpora

import string
import os
import json


# The Enron Mobile Email Dataset (Vertanen & Kristensson)
# https://doi.org/10.1145/2037373.2037418
def read_enron(folder):
    corpus = []
    dir_path = folder
    for path in os.scandir(dir_path):
        if path.is_file():
            with open(path) as f:
                for line in f:
                    line = line.split('\t')[1]
                    line= line.translate(str.maketrans('', '', string.punctuation)).strip().lower()
                    line = ''.join([i for i in line if not i.isdigit()])
                    corpus.append(line)
    return(corpus)


# Representatively memorable: sampling the right phrase set to get the text entry experiment right (Leiva & Sanchis-Trilles)
# https://doi.org/10.1145/2556288.2557024
# https://luis.leiva.name/memrep/
# No punctuation & lowercased-tokenized English phrase set

def read_leiva(file):
    corpus=[]
    with open(file) as f:
        for line in f:
            line= line.translate(str.maketrans('', '', string.punctuation)).strip().lower()
            line = ''.join([i for i in line if not i.isdigit()])
            corpus.append(line)
    return corpus


# Phrase sets for evaluating text entry techniques (MacKenzie & Soukoreff)
# https://doi.org/10.1145/765891.765971
# https://luis.leiva.name/memrep/data/phrases-en-mackenzie.txt

def read_soukoreff(file):
    corpus=[]
    with open(file) as f:
        for line in f:
            line= line.translate(str.maketrans('', '', string.punctuation)).strip().lower()
            line = ''.join([i for i in line if not i.isdigit()])
            corpus.append(line)
    return corpus


# Creating a live, public short message service corpus: the NUS SMS corpus (Chen & Kan)
# https://doi.org/10.1007/s10579-012-9197-9
# https://scholarbank.nus.edu.sg/handle/10635/137343

def read_singapore():
    corpus=[]
    with open(file) as f:
        data = json.load(f)
        data = data['smsCorpus']['message']
        for msg in data:
            line = str(msg['text']["$"])
            line = line.translate(str.maketrans('', '', string.punctuation)).strip().lower()
            line = ''.join([i for i in line if not i.isdigit()])
            corpus.append(line)
            print(line+'--')
    return corpus

# Create a corpus from a single sentence, repeated n times
def read_sentence(sentence, reps):
    corpus=[]
    for i in range(reps):
        corpus.append(sentence)
    return corpus
