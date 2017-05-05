import nltk.data
import re
import os
import pickle
import pymorphy2


class CleanText:
    def __init__(self, dir, tokenizer, normalize=None):
        self.normalize = normalize
        self.tokenizer = tokenizer
        self.dir = dir
        self.data = None

    def __open_file(self, path):
        print("Open {}".format(path))
        with open(path, 'r') as file:
            data = file.read()
        return data

    def __sentence_to_wordlist(self, sentence):
        sentence = re.sub("[\W\d]+", " ", sentence)
        if self.normalize is not None:
            words = [self.normalize.parse(word)[0].normal_form for word in sentence.split() if len(word) > 2]
        else:
            words = [word for word in sentence.split() if len(word) > 2]
        return words

    def __text_to_sentences(self, data):
        raw_sentences = self.tokenizer.tokenize(data.strip())
        sentences = []
        for raw_sentence in raw_sentences:
            if len(raw_sentence) > 0:
                sentences.append(self.__sentence_to_wordlist(raw_sentence))
        return sentences

    def __listdir_nohidden(self, path):
        for i in os.listdir(path):
            if not i.startswith('.'):
                yield i

    def run(self):
        print("Processing...")
        for d in self.__listdir_nohidden(self.dir):
            data = ""
            for file in self.__listdir_nohidden(self.dir + "/" + d):
                if file.endswith(".txt"):
                    data += self.__open_file(self.dir + "/" + d + "/" + file)
            if self.normalize is not None:
                pickle.dump(self.__text_to_sentences(data), open(self.dir + "/" + d + "/" + d + "_norm.p", "wb"))
            else:
                pickle.dump(self.__text_to_sentences(data), open(self.dir + "/" + d + "/" + d + ".p", "wb"))
        print("Done.")


tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
morph = pymorphy2.MorphAnalyzer()
current_dir = "Authors"

cl = CleanText(current_dir, tokenizer, normalize=morph)
cl.run()
