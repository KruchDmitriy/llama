import os
import gensim
import smart_open
import random
import pickle
from gensim.models.doc2vec import Doc2Vec

book = 'Strugatsky.p'
model_file = 'strug.d2v'


def read_corpus(data):
    for i, line in enumerate(data):
        yield gensim.models.doc2vec.TaggedDocument(line, [i])


if __name__ == '__main__':
    with open(book, 'rb') as f:
        data = pickle.load(f)

    corpus = list(read_corpus(data))

    if (os.path.isfile(model_file)):
        model = Doc2Vec.load(model_file)
    else:
        model = gensim.models.doc2vec.Doc2Vec(size=300, iter=50)
        model.build_vocab(corpus)

        for epoch in range(10):
            print("train epoch: " + str(epoch))
            model.train(corpus, total_examples=model.corpus_count)
            model.alpha -= 0.002
            model.min_alpha = model.alpha

        model.save(model_file)

    sentence = ['И', 'тогда', 'я', 'пошел', 'зарабатывать', 'для', 'того',
                'чтобы', 'выжить']

    inferred_vector = model.infer_vector(sentence)
    print(inferred_vector)

    sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
    print(sims[:10])

    # Compare and print the most similar documents from the train corpus
    for index in range(10):
        print(u'%s %s: «%s»\n' % (index, sims[index], ' '.join(corpus[sims[index][0]].words)))
