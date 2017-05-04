import json
import pickle
import semantics as sem


def read_data_model(file_name: str) -> dict:
    file = open(file_name, mode='r', encoding='utf-8')
    return json.load(file)


def write_data_model(file_name: str, data_model: dict):
    file = open(file_name, mode='w', encoding='utf-8')
    json.dump(data_model, file, separators=(',', ':'), ensure_ascii=False)


def read_phrases(file_name: str) -> list:
    file = open(file_name, encoding='utf-8')
    lines = file.readlines()
    phrases = []
    phrase = ""
    for line in lines:
        if len(line.strip()) == 0:
            if len(phrase.strip()) > 0:
                phrases.append(phrase.lower())
                phrase = ""
        else:
            phrase += line
    return phrases


def read_pickle(file_name: str) -> list:
    with open(file_name, 'rb') as f:
        phrases = [' '.join(words) for words in pickle.load(f)]
        return phrases


def make_bags(texts: list) -> (list, dict):
    bags = []
    vocabulary = {}
    for txt in texts:
        bag = []
        words = sem.canonize_words(txt.split())
        for w in words:
            if w not in bag:
                bag.append(w)
            vocabulary[w] = vocabulary.get(w, 0) + 1
        bags.append(bag)
    return bags, vocabulary


def empty_model() -> dict:
    return {'phrases': [],
            'bags': [],
            'vocabulary': {},
            'density': [],
            'associations': [],
            'rates': []}


def make_phrases_model(file_name: str, semantics=True) -> dict:
    print("making phrases model...")
    phrases = read_pickle(file_name)
    print('phrases count:', len(phrases))
    bags, voc = make_bags(phrases)
    sa = []
    sd = []
    if semantics:
        print("loading w2v_model...")
        w2v_model = sem.load_w2v_model(sem.WORD2VEC_MODEL_FILE)
        print("adding semantics to model...")
        sd = [sem.semantic_density(bag, w2v_model, unknown_coef=-0.001) for bag in bags]
        sa = [sem.semantic_association(bag, w2v_model) for bag in bags]
    rates = [0.0 for _ in range(len(phrases))]
    print("model created")
    return {'phrases': phrases,
            'bags': bags,
            'vocabulary': voc,
            'density': sd,
            'associations': sa,
            'rates': rates}


def append_model_to_model(head_model, tail_model):
    for w in tail_model['vocabulary'].keys():
        head_model['vocabulary'][w] = head_model['vocabulary'].get(w, 0) + tail_model['vocabulary'][w]
        phrases_len = len(tail_model['phrases'])
        dens_len = len(tail_model['density'])
        assoc_len = len(tail_model['associations'])
        rates_len = len(tail_model['rates'])
    for i in range(phrases_len):
        if tail_model['bags'][i] not in head_model['bags']:
            head_model['phrases'].append(tail_model['phrases'][i])
            head_model['bags'].append(tail_model['bags'][i])
            if dens_len == phrases_len:
                head_model['density'].append(tail_model['density'][i])
            if assoc_len == phrases_len:
                head_model['associations'].append(tail_model['associations'][i])
            if rates_len == phrases_len:
                head_model['rates'].append(tail_model['rates'][i])
        else:
            print('<!!!>\n', tail_model['phrases'][i])


def print_phrases_model(phrases_model):
    print("phrases: ", phrases_model['phrases'])
    print("bags: ", phrases_model['bags'])
    print("vocabulary: ", phrases_model['vocabulary'])
    print("density: ", phrases_model['density'])
    print("associations: ", phrases_model['associations'])
    print("rates: ", phrases_model['rates'])


def load_phrases_model(file_name, w2v_model, vectorize=True):
    pmodel = read_data_model(file_name)
    print("loading model...")
    if vectorize:
        print("vectorizing model...")
        pmodel['matrices'] = [sem.bag_to_matrix(bag, w2v_model) for bag in pmodel['bags']]
        pmodel['a_matrices'] = [sem.bag_to_matrix(bag, w2v_model) for bag in pmodel['associations']]
    print("phrases model '%s' loaded" % file_name)
    return pmodel


def save_phrases_to_file(phrase_model, file_name):
    f_out = open(file_name, mode='w', encoding='utf-8')
    for phrase in phrase_model['phrases']:
        f_out.write(phrase + '\n')


if __name__ == "__main__":
    phrases_model = make_phrases_model("data/Strugatsky.p")
    pm_file = "data/strugatsky.dat"
    write_data_model(pm_file, phrases_model)
    print("model was saved to file '%s'" % pm_file)

