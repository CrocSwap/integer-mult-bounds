# positive control for cnt8's support filter: the removed-frame coordinate decoder (8 terms, rows/cols live off the survivor classes
# N(f) = lines ⊥ f) plus an empty ninth term must pass (D) and (C); dropping a term must fail.
import sys
sys.argv = sys.argv[:2]
from m9lib import *
cliques = [sum(1 << t for t in c) for c in pickle.load(open(f'cliques_{unit}.pkl', 'rb')) if len(c) in (7, 8)]
def test(terms):
    cover = 0
    for r_, a_ in terms: cover |= r_ & a_
    return cover == full, all(sum(1 for r_, a_ in terms if r_ & Cq and a_ & Cq) >= pc(Cq) for Cq in cliques)
T = [(full ^ cls[s], full ^ cls[s]) for s in surv]
print('coordinate decoder + empty term:', test(T + [(0, 0)]), '| drop one term:', test(T[1:] + [(0, 0), (0, 0)]))
