"""All root hyperplanes of E8 by type, as W(E8)-orbits of one normal each (exact integer vectors, hamming coords)."""
import numpy as np, pickle, random
from fractions import Fraction
from math import gcd
from functools import reduce
from geo import *
from sympy import Matrix
def prim(v):
    v = [int(x) for x in v]; g = reduce(gcd, [abs(x) for x in v if x] or [1]); v = [x // g for x in v]
    i = next(i for i, x in enumerate(v) if x)
    return tuple(-x for x in v) if v[i] < 0 else tuple(v)
def refl_vec(x, r):
    # s_r(x) = x - 2 (x.r)/(r.r) r ; roots norm 4 in hamming coords
    x = np.array(x, dtype=object); r = np.array(r, dtype=object)
    num = 2 * int(x @ r); den = int(r @ r)
    y = x * den - num * r
    return prim(y)
def orth_mask(n):
    n = np.array(n, dtype=np.int64)
    return sum(1 << i for i in range(NL) if int(L[i] @ n) == 0)
def find_types(seed=1, trials=60000):
    rng = random.Random(seed); reps = {}
    for _ in range(trials):
        idx = rng.sample(range(NL), 7)
        M = Matrix(L[idx].tolist())
        if M.rank() < 7: continue
        n = prim([x * reduce(lambda a, b: a * b // gcd(a, b), [t.q for t in M.nullspace()[0]]) for x in M.nullspace()[0]])
        sz = bin(orth_mask(n)).count('1')
        if sz not in reps: reps[sz] = n
        if len(reps) == 8: break
    return reps
def orbit(n0):
    seen = {n0}; frontier = [n0]
    while frontier:
        nf = []
        for n in frontier:
            for r in range(NL):
                m = refl_vec(n, L[r])
                if m not in seen: seen.add(m); nf.append(m)
        frontier = nf
    return sorted(seen)
if __name__ == '__main__':
    reps = find_types()
    print({k: v for k, v in sorted(reps.items())})
    H = {}
    for sz in sorted(reps, reverse=True):
        if sz < 28: continue
        orb = orbit(reps[sz]); H[sz] = [(n, orth_mask(n)) for n in orb]
        print(sz, len(orb), flush=True)
    pickle.dump(H, open('hyper.pkl', 'wb'))
