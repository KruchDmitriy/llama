import pymorphy2
import gensim
import pickle
import numpy as np
from gensim.similarities import WmdSimilarity
from gensim.models.phrases import Phrases

from scipy.spatial import distance

import nltk
from nltk.collocations import *
from nltk import ngrams


model_file = '../models/model.bin.gz'


def load_model(filename):
    return gensim.models.KeyedVectors.load_word2vec_format(filename, binary=True)


def normalize_text(text):
    morph = pymorphy2.MorphAnalyzer()
    norm_text = []
    for sent in text:
        norm_sent = []
        for word in sent:
            norm_word = morph.parse(word)[0].normal_form
            norm_sent.append(norm_word)
        norm_text.append(norm_sent)

    return norm_text


def normalize_ngram(ngram):
    morph = pymorphy2.MorphAnalyzer()
    norm_ngram = []
    for gram in ngram:
        norm_gram = morph.parse(gram)[0].normal_form
        norm_ngram.append(norm_gram)
    return norm_ngram


def distance(ngram1, ngram2, model):
    avg_vec1 = np.zeros(shape=model.syn0.shape[1])
    for gram in ngram1:
        avg_vec1 += np.array(model[gram])
    avg_vec1 /= len(ngram1)

    avg_vec2 = np.zeros(shape=model.syn0.shape[1])
    for gram in gram1:
        avg_vec2 += np.array(model[gram])
    avg_vec2 /= len(ngram2)

    return distance(avg_vec1, avg_vec2)


def find_closest_ngram(gram, ngrams, model):
    dist = []
    for ngram in ngrams:
        dist.append(model.wmdistance(gram, ngram))

    idx = np.argmin(np.array(dist))

    return trigrams[idx], dist[idx]


if __name__ == "__main__":
    files = ['Strugatsky.p', 'TolstoyLev.p', 'Dostoevsky.p', 'Pushkin.p']

    text = []
    for file in files:
        with open(file, 'rb') as f:
            text = text + pickle.load(f)

    bigram_measures = nltk.collocations.BigramAssocMeasures()
    trigram_measures = nltk.collocations.TrigramAssocMeasures()

    words = [val for sublist in text for val in sublist]

    finder = TrigramCollocationFinder.from_words(words)
    finder.apply_freq_filter(2)
    trigrams = finder.nbest(trigram_measures.pmi, 100000)

    finder = BigramCollocationFinder.from_words(words)
    finder.apply_freq_filter(2)
    bigrams = finder.nbest(bigram_measures.pmi, 100000)

    norm_bigrams = normalize_text(bigrams)
    norm_trigrams = normalize_text(trigrams)

    model = load_model(model_file)
    model.init_sims(True)

    print("I am ready!")
    while True:
        string = str(input())
        if string == "exit":
            break

        cur_ngrams = ngrams(string.split(), 3)
        closest = []
        for ngram in cur_ngrams:
            norm_ngram = normalize_ngram(ngram)
            bigram, score2 = find_closest_ngram(norm_ngram, norm_bigrams, model)
            trigram, score3 = find_closest_ngram(norm_ngram, norm_trigrams, model)
            if score2 < score3:
                closest.append(bigram)
            else:
                closest.append(trigram)

        print(closest)
