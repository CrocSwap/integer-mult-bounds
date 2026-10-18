"""Balanced-D4 mechanism census. Every E8 frame meets complementary coordinate D4 subsystems equally. For each
D4+D4 split S=(Da,Db) containing FRAME0 4+4 (the coordinate splits and their images under the FRAME0 stabiliser
generators), each pivot frame F disjoint from FRAME0 and each pivot k, take the smallest deletion X that makes every
live non-pivot line of Da u Db odd to F[k], and run PR1650's criterion at (X, F)."""
import os
import sys, collections, itertools
sys.path.insert(0, os.environ['PR1650_PACKAGE'])  # research/complex-rank8-rigidity-p105 at PR1650 head d960f8a2
import verify as V
from concurrent.futures import ProcessPoolExecutor

def half(h):
    return frozenset(i for i, v in enumerate(V.LINES) if all(v[j] == 0 for j in range(8) if j not in h))

pairs = [(0, 1), (2, 3), (4, 5), (6, 7)]
splits0 = set()
for a in itertools.combinations(range(4), 2):
    ha = [c for p in a for c in pairs[p]]; hb = [c for c in range(8) if c not in ha]
    splits0.add(frozenset([half(ha), half(hb)]))
def all_splits():
    gens = V.stabiliser(V.FRAME0)
    seen = set(splits0); todo = list(splits0)
    while todo:
        s = todo.pop()
        for g in gens:
            t = frozenset(frozenset(g[i] for i in d) for d in s)
            if t not in seen:
                seen.add(t); todo.append(t)
    return [tuple(s) for s in seen]

def check_identity(splits):
    for Da, Db in splits:
        assert all(len(set(F) & Da) == len(set(F) & Db) for F in V.FRAMES)
        assert len(V.FRAME0 & Da) == 4 and len(V.FRAME0 & Db) == 4

def job(arg):
    splits, p = arg
    F = V.FRAMES[p]; out = []
    for Da, Db in splits:
        U = (Da | Db) - V.FRAME0 - set(F)
        for k in range(8):
            X = tuple(sorted(i for i in U if V.G[i][F[k]] == 0))
            if not X:
                continue
            r = V.criterion(X, F)[0]
            out.append((len(X), r, p, k, X))
    return out

if __name__ == '__main__':
    S = all_splits(); check_identity(S)
    print('splits', len(S))
    piv = [n for n, m in enumerate(V.FMASK) if not m & V.F0MASK]
    print('pivots', len(piv))
    tally = collections.Counter(); best = {}
    with ProcessPoolExecutor(6) as ex:
        for out in ex.map(job, [(S, p) for p in piv], chunksize=16):
            for n, r, p, k, X in out:
                tally[(n, r)] += 1
                if r == 'D' and (n not in best):
                    best[n] = (p, k, X)
    print(sorted(tally.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))))
    print('first D example per |X|', best)
