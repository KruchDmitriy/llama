import semantics as sem
import make_phrases_model as mpm
import analyze_phrase as ap
from pprint import pprint

w2v_model = sem.load_w2v_model(sem.WORD2VEC_MODEL_FILE)
phrases_model = mpm.load_phrases_model("data/strugatsky.dat", w2v_model, vectorize=True)
pprint(ap.similar_phrases("жизнь", phrases_model, w2v_model, top_n=5, use_associations=False))
