# Loads the two orthogonal frames F0 (removed for P112) and F1 (additionally removed for P104) from ../data/p104_frames.json and re-derives
# their indices in the E8 line list from the explicit vectors (asserts the stored indices agree as sets).
import json, os
from fractions import Fraction as Fr
from lib import lines, e8_roots, dot
def load_frames():
    d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'p104_frames.json')))
    E8 = lines(e8_roots())
    def canon(x):
        for c in x:
            if c != 0: return tuple(x) if c > 0 else tuple(-y for y in x)
    idx = {canon(r): i for i, r in enumerate(E8)}
    def vec(*pairs):
        r = [Fr(0)] * 8
        for i, s in pairs: r[i] = Fr(s)
        return r
    F0 = [idx[canon(vec((2 * a, 1), (2 * a + 1, 1)))] for a in range(4)] + [idx[canon(vec((2 * a, 1), (2 * a + 1, -1)))] for a in range(4)]
    F1 = [idx[canon([Fr(x, 2) for x in w])] for w in d['F1_vectors_x2']]
    assert F0 == d['F0_idx'] and set(F1) == set(d['F1_idx']) and len(set(F0) | set(F1)) == 16
    for F in (F0, F1): assert all(dot(E8[a], E8[b]) == 0 for a in F for b in F if a != b)
    return list(F0), list(d['F1_idx'])
