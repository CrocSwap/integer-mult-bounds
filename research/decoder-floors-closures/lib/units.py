"""The E8-family units used throughout this package (standard library only; built on lib/roots.py).
E8 = 120 lines in doubled coordinates (lib/roots.py order).  F0 = the frame {2e_{2k} +- 2e_{2k+1}} (k = 0..3), the removed frame of P112.
P112 = E8 minus F0 (112 lines).  P104 = P112 minus a second frame F1 disjoint from F0 (104 lines).  H4 = the F1 of #968 (data/h4_F1.json).
E7 = lines orthogonal to line 0 (63); E6 = lines orthogonal to line 0 and to the first line non-orthogonal to line 0 (36)."""
import json, os
from roots import *

_UH = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(_UH, '..', 'data')
IDX = {r: i for i, r in enumerate(E8)}
def idx(v):
    v = tuple(v); w = tuple(-x for x in v)
    return IDX[v] if v in IDX else IDX[w]
F0 = []
for _k in range(4):
    for _s in (2, -2):
        _v = [0] * 8; _v[2 * _k] = 2; _v[2 * _k + 1] = _s; F0.append(idx(_v))
F0 = sorted(F0)
H4F1 = sorted(idx(v) for v in json.load(open(os.path.join(DATA, 'h4_F1.json'))))
GE8 = gram(E8)
def orth(t, s): return GE8[t][s] == 0
def sub(ix): return [E8[i] for i in ix]
P112_IDX = [i for i in range(120) if i not in set(F0)]
def p104_idx(F1): return [i for i in P112_IDX if i not in set(F1)]
def p104_reps():
    d = json.load(open(os.path.join(DATA, 'p104reps.json')))
    return {int(k[1:k.index(',')]): v for k, v in d.items()}      # frame count (759, 767, 801) -> F1 as E8 indices
_b = next(t for t in range(1, 120) if GE8[t][0] != 0)
E7_IDX = [t for t in range(120) if GE8[t][0] == 0 and t != 0]
E6_IDX = [t for t in range(120) if GE8[t][0] == 0 and GE8[t][_b] == 0 and t not in (0, _b)]
def unit_idx(name):
    if name == 'E8': return list(range(120))
    if name == 'P112': return list(P112_IDX)
    if name == 'P104H4': return p104_idx(H4F1)
    if name.startswith('P104_'): return p104_idx(p104_reps()[int(name[5:])])
    if name == 'E7': return list(E7_IDX)
    if name == 'E6': return list(E6_IDX)
    raise KeyError(name)
