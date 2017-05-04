from gensim.models.keyedvectors import KeyedVectors
import logging
import numpy as np
import re
import click


def load_w2v_model(file_name: str):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    w2v_model = KeyedVectors.load_word2vec_format(file_name, binary=True, encoding='utf-8')
    print("word2vec model '%s' loaded" % file_name)
    return w2v_model


def save_w2v_model(file_name: str, w2v_model: KeyedVectors):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    w2v_model.save_word2vec_format(file_name, binary=True)
    print("word2vec model '%s' saved" % file_name)
    return w2v_model


def clear_word(word):
    under_idx = word.find('_')
    return word[:under_idx] if under_idx >= 0 else word


def is_word_dirty(word, re_exp):
    under_idx = word.find('_')
    if under_idx >= 0:
        word = word[:under_idx].upper()
        if re.match(re_exp, word):
            return False
    return True


def delete_keys(w2v_model: KeyedVectors, del_keys: list):
    del_indexes = []
    with click.progressbar(del_keys, length=len(del_keys), label='Deleted keys') as bar:
        for key in bar:
            del_idx = w2v_model.vocab[key].index
            del_indexes.append(del_idx)
            del w2v_model.vocab[key]
            w2v_model.index2word[del_idx] = ''
    w2v_model.syn0 = np.delete(w2v_model.syn0, del_indexes, axis=0)
    w2v_model.index2word = [word for word in w2v_model.index2word if word]
    for i, word in enumerate(w2v_model.index2word):
        w2v_model.vocab[word].index = i
    print(len(model.vocab), w2v_model.syn0.shape)


def thin_w2vec_model(w2v_model: KeyedVectors):
    re_rus_word = re.compile('^[А-Я\-]+$')
    dirty_keys = [model.index2word[idx]
                  for idx in range(len(model.index2word))
                  if is_word_dirty(model.index2word[idx], re_exp=re_rus_word)]
    print('deleting dirty keys...')
    delete_keys(w2v_model, dirty_keys)


if __name__ == "__main__":
    model = load_w2v_model('data/ruscorpora.bin.gz')
    thin_w2vec_model(model)
    save_w2v_model('data/ruscorpora.bin_thin.gz', model)
