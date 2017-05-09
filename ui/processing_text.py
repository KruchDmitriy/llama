# -*- coding: utf-8 -*-

import re
import gensim
import pymorphy2
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

model = gensim.models.KeyedVectors.load_word2vec_format('../models/model.bin.gz', binary=True)
model.init_sims(replace=True)

morph = pymorphy2.MorphAnalyzer()
punctuation_regexp = re.compile('^(.*?)([а-яА-ЯёЁ-]+)(.*?)$')
capital_regexp = re.compile('^[А-Я]+$')

pth_source = 'books_before/'
pth_result = 'books_result/'

cotags = {'ADJF': 'ADJ',  # pymorphy2: word2vec
          'ADJS': 'ADJ',
          'ADVB': 'ADV',
          'COMP': 'ADV',
          'GRND': 'VERB',
          'INFN': 'VERB',
          'NOUN': 'NOUN',
          'PRED': 'ADV',
          'PRTF': 'ADJ',
          'PRTS': 'VERB',
          'VERB': 'VERB'}

capit_letters = [chr(x) for x in range(1040, 1072)] + ['Ё']


def search_neighbour(word, pos, gend='masc'):
    word = word.replace('ё', 'е')
    lex = word + '_' + cotags[pos]
    if lex in model:
        neighbs = model.most_similar([lex], topn=20)
        for neighbour in neighbs:
            lex_n, ps_n = neighbour[0].split('_')
            if '::' in lex_n:
                continue
            if cotags[pos] == ps_n:
                if pos == 'NOUN':
                    parse_result = morph.parse(lex_n)
                    for ana in parse_result:
                        if ana.normal_form == lex_n:
                            if ana.tag.gender == gend:
                                return lex_n
                elif cotags[pos] == 'VERB' and word[-2:] == 'ся':
                    if lex_n[-2:] == 'ся':
                        return lex_n
                elif cotags[pos] == 'VERB' and word[-2:] != 'ся':
                    if lex_n[-2:] != 'ся':
                        return lex_n
                else:
                    return lex_n
    return None


def flection(lex_neighb, tags):
    tags = str(tags)
    tags = re.sub(',[AGQSPMa-z-]+? ', ',', tags)
    tags = tags.replace("impf,", "")
    tags = re.sub('([A-Z]) (plur|masc|femn|neut|inan)', '\\1,\\2', tags)
    tags = tags.replace("Impe neut", "")
    tags = tags.split(',')

    tags_clean = []
    for tag in tags:
        if tag and ' ' in tag:
            _, tag = tag.split(' ')
            tags_clean.append(tag)

    tags = frozenset(tags_clean)

    prep_for_gen = morph.parse(lex_neighb)
    info_words = []
    for info in prep_for_gen:
        if info.normal_form == lex_neighb:
            info_words.append(info)
    for info in info_words:
        try:
            flect = info.inflect(tags)
        except:
            print("oops" + str(tags))
            return None
        if flect:
            word_to_replace = flect.word
            return word_to_replace
    return None


def parse_with_punctuation(before_punct, word, after_punct, was_capital):
    if was_capital:
        word = word.capitalize()
    return before_punct + word + after_punct


def parse_nominative(word, parse_result, was_capital, lex_neighb, punct):
    if parse_result.tag.case == 'nomn' and parse_result.tag.number == 'sing':
        return parse_with_punctuation(punct[0], lex_neighb, punct[2], was_capital)

    word_to_replace = flection(lex_neighb, parse_result.tag)
    if word_to_replace:
        return parse_with_punctuation(punct[0], word_to_replace, punct[2], was_capital)

    return word


def process_word(word, cash_neighb):
    struct = punctuation_regexp.findall(word)
    if struct:
        struct = struct[0]
    else:
        return word

    word_form = struct[1]
    if word_form:
        if capital_regexp.search(word_form):
            return word

        was_capital = word_form[0] in capit_letters

        parse_result = morph.parse(word_form)[0]
        if 'Name' in parse_result.tag \
                or 'Patr' in parse_result.tag \
                or parse_result.normal_form == 'глава':
            return word

        pos_flag = False
        for tag in cotags:
            if tag in parse_result.tag:
                pos_flag = True
                lex = parse_result.normal_form
                pos_tag = parse_result.tag.POS

                if (lex, pos_tag) in cash_neighb:
                    lex_neighb = cash_neighb[(lex, pos_tag)]
                else:
                    if pos_tag == 'NOUN':
                        gen_tag = parse_result.tag.gender
                        lex_neighb = search_neighbour(lex, pos_tag, gend=gen_tag)
                    else:
                        lex_neighb = search_neighbour(lex, pos_tag)
                    cash_neighb[(lex, pos_tag)] = lex_neighb

                if not lex_neighb:
                    return word

                if pos_tag in ['NOUN', 'ADJF']:
                    return parse_nominative(word, parse_result, was_capital, lex_neighb, struct)

                if pos_tag in ['INFN', 'ADVB', 'COMP', 'PRED']:
                    return parse_with_punctuation(struct[0], lex_neighb, struct[2], was_capital)

                word_to_replace = flection(lex_neighb, parse_result.tag)
                if word_to_replace:
                    return parse_with_punctuation(struct[0], word_to_replace, struct[2], was_capital)

                return word
        if not pos_flag:
            return word
    else:
        return ''.join(struct)


def run(text):
    cash_neighbours = {}
    words = text.split(' ')
    result_text = ""
    for word in words:
        result_text += process_word(word, cash_neighbours) + ' '
    return result_text


def main():
    while True:
        text = str(input())
        print(run(text))


main()
