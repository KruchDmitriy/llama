import os
import re
import gensim
import pymorphy2
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Processing:
    def __init__(self, model):
        self.model = gensim.models.KeyedVectors.load_word2vec_format(model, binary=True)
        self.model.init_sims(replace=True)
        self.morph = pymorphy2.MorphAnalyzer()
        self.punct = re.compile('^(.*?)([а-яА-ЯёЁ-]+)(.*?)$')
        self.capit = re.compile('^[А-Я]+$')
        self.cotags = {'ADJF': 'ADJ',
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
        self.capit_letters = [chr(x) for x in range(1040, 1072)] + ['Ё']
        self.cash_neighb = {}

    def __search_neighbour(self, word, pos, gend='masc'):
        word = word.replace('ё', 'е')
        lex = word + '_' + self.cotags[pos]
        if lex in self.model:
            neighbs = self.model.most_similar([lex], topn=20)
            for nei in neighbs:
                lex_n, ps_n = nei[0].split('_')
                if '::' in lex_n:
                    continue
                if self.cotags[pos] == ps_n:
                    if pos == 'NOUN':
                        parse_word = self.morph.parse(lex_n)
                        for ana in parse_word:
                            if ana.normal_form == lex_n:
                                if ana.tag.gender == gend:
                                    return lex_n
                    elif self.cotags[pos] == 'VERB' and word[-2:] == 'ся':
                        if lex_n[-2:] == 'ся':
                            return lex_n
                        elif self.cotags[pos] == 'VERB' and word[-2:] != 'ся':
                            if lex_n[-2:] != 'ся':
                                return lex_n
                            else:
                                return lex_n
        return None

    def __flection(self, lex_neighb, tags):
        tags = str(tags)
        tags = re.sub(',[AGQSPMa-z-]+? ', ',', tags)
        tags = tags.replace("impf,", "")
        tags = re.sub('([A-Z]) (plur|masc|femn|neut|inan)', '\\1,\\2', tags)
        tags = tags.replace("Impe neut", "")
        tags = tags.split(',')
        tags_clean = []
        for t in tags:
            if t:
                if ' ' in t:
                    t1, t2 = t.split(' ')
                    t = t2
                tags_clean.append(t)
        tags = frozenset(tags_clean)
        prep_for_gen = self.morph.parse(lex_neighb)
        ana_array = []
        for ana in prep_for_gen:
            if ana.normal_form == lex_neighb:
                ana_array.append(ana)
        for ana in ana_array:
            try:
                flect = ana.inflect(tags)
            except:
                print(tags)
                return None
            if flect:
                word_to_replace = flect.word
                return word_to_replace
        return None

    def __parse_tags(self, struct, word, new_line, parse_word, capit_flag):
        pos_flag = 0
        for tg in self.cotags:
            if tg in parse_word.tag:
                pos_flag = 1
                lex = parse_word.normal_form
                pos_tag = parse_word.tag.POS
                if (lex, pos_tag) in self.cash_neighb:
                    lex_neighb = self.cash_neighb[(lex, pos_tag)]
                else:
                    if pos_tag == 'NOUN':
                        gen_tag = parse_word.tag.gender
                        lex_neighb = self.__search_neighbour(lex, pos_tag, gend=gen_tag)
                    else:
                        lex_neighb = self.__search_neighbour(lex, pos_tag)
                    self.cash_neighb[(lex, pos_tag)] = lex_neighb
                if not lex_neighb:
                    new_line.append(word)
                    break
                else:
                    if pos_tag == 'NOUN':
                        if parse_word.tag.case == 'nomn' and parse_word.tag.number == 'sing':
                            if capit_flag == 1:
                                lex_neighb = lex_neighb.capitalize()
                            new_line.append(struct[0] + lex_neighb + struct[2])
                        else:
                            word_to_replace = self.__flection(lex_neighb, parse_word.tag)
                            if word_to_replace:
                                if capit_flag == 1:
                                    word_to_replace = word_to_replace.capitalize()
                                new_line.append(struct[0] + word_to_replace + struct[2])
                            else:
                                new_line.append(word)
                    elif pos_tag == 'ADJF':
                        if parse_word.tag.case == 'nomn' and parse_word.tag.number == 'sing':
                            if capit_flag == 1:
                                lex_neighb = lex_neighb.capitalize()
                            new_line.append(struct[0] + lex_neighb + struct[2])
                        else:
                            word_to_replace = self.__flection(lex_neighb, parse_word.tag)
                            if word_to_replace:
                                if capit_flag == 1:
                                    word_to_replace = word_to_replace.capitalize()
                                new_line.append(struct[0] + word_to_replace + struct[2])
                            else:
                                new_line.append(word)
                    elif pos_tag == 'INFN':
                        if capit_flag == 1:
                            lex_neighb = lex_neighb.capitalize()
                        new_line.append(struct[0] + lex_neighb + struct[2])
                    elif pos_tag in ['ADVB', 'COMP', 'PRED']:
                        if capit_flag == 1:
                            lex_neighb = lex_neighb.capitalize()
                        new_line.append(struct[0] + lex_neighb + struct[2])

                    else:
                        word_to_replace = self.__flection(lex_neighb, parse_word.tag)
                        if word_to_replace:
                            if capit_flag == 1:
                                word_to_replace = word_to_replace.capitalize()
                            new_line.append(struct[0] + word_to_replace + struct[2])
                        else:
                            new_line.append(word)
                break
        return new_line, pos_flag

    def __words_parse(self, words, new_line):
        for word in words:
            struct = self.punct.findall(word)
            if struct:
                struct = struct[0]
            else:
                new_line.append(word)
                continue
            word_form = struct[1]
            if word_form:
                if self.capit.search(word_form):
                    new_line.append(word)
                    continue
                else:
                    if word_form[0] in self.capit_letters:
                        capit_flag = 1
                    else:
                        capit_flag = 0
                parse_word = self.morph.parse(word_form)[0]
                if 'Name' in parse_word.tag or 'Patr' in parse_word.tag:
                    new_line.append(word)
                    continue
                if parse_word.normal_form == 'глава':
                    new_line.append(word)
                    continue
                new_line, pos_flag = self.__parse_tags(struct, word, new_line, parse_word, capit_flag)
                if pos_flag == 0:
                    new_line.append(word)
            else:
                new_line.append(''.join(struct))
        return new_line

    def run(self, path_source, path_result):
        print("Processing...")
        files = os.listdir(path_source)
        for file in files:
            print("Parse file: {}".format(file))
            with open(path_source + file, 'r', encoding='utf-8') as data, \
                    open(path_result + "out-" + file, 'w') as out:
                lines = data.readlines()
                for line in lines:
                    new_line = []
                    line = line.strip()
                    words = line.split(' ')
                    new_line = self.__words_parse(words, new_line)
                    line_replace = ' '.join(new_line)
                    out.write(line_replace + '\n')

a = Processing('ruwikiruscorpora_0_300_20.bin')
a.run('books_before/', 'books_result/')