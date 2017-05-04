import numpy as np
import semantics as sem
import heapq


def similar_phrases_idx(query: str, phrase_model, w2v_model, top_n=5, use_associations=False) -> list:
    query_bag = sem.canonize_words(query.split())
    if use_associations:
        query_bag += sem.semantic_association(query_bag, w2v_model, top_n=5)
        query_mx = sem.bag_to_matrix(query_bag, w2v_model)
        if len(query_mx) == 0:
            return []
        similars = [(i, sem.semantic_similarity_fast(query_mx, np.vstack((mx, phrase_model['a_matrices'][i]))))
                    for i, mx in enumerate(phrase_model['matrices']) if len(mx) > 0]
    else:
        query_mx = sem.bag_to_matrix(query_bag, w2v_model)
        if len(query_mx) == 0:
            return []
        similars = [(i, sem.semantic_similarity_fast_log(query_mx, mx))
                    for i, mx in enumerate(phrase_model['matrices'])]
    return heapq.nlargest(top_n, similars, key=lambda x: x[1])


def similar_phrases(query: str, phrase_model, w2v_model, top_n=5, use_associations=False) -> list:
    return [(phrase_model['phrases'][idx], sim)
            for idx, sim in similar_phrases_idx(query, phrase_model, w2v_model, top_n, use_associations)]


def rate_phrase(phrase: str, phrase_model: dict, w2v_model, nearest=20) -> float:
    similars = similar_phrases_idx(phrase, phrase_model, w2v_model, nearest)
    res_rate = 0.0
    sim_sum = 0.0
    for idx, sim in similars:
        rate = phrase_model['rates'][idx]
        if sim > 0:
            res_rate += rate * sim
            sim_sum += sim
    if sim_sum > 0:
        return res_rate / sim_sum
    else:
        return 0.0


def print_phrases_by_density(phrases_model: dict):
    sd = phrases_model['density']
    sa = phrases_model['associations']
    lsd = list(enumerate(sd))
    lsd.sort(key=lambda x: x[1])
    for i in range(1, 10):
        print(phrases_model['phrases'][lsd[-i][0]], lsd[-i][1])
        print(phrases_model['bags'][lsd[-i][0]])
        print(sa[lsd[-i][0]], "\n")
    for i in range(0, 10):
        print(phrases_model['phrases'][lsd[i][0]], lsd[i][1])
        print(phrases_model['bags'][lsd[i][0]])
        print(sa[lsd[i][0]], "\n")
