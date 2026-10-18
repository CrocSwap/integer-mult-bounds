# Fast equivalent of paircensus.py (same output file pairs_UNIT.pkl, same pair order): the pairs (z <= z') of label classes whose intersection
# O_z ∩ O_z' is NOT certified spanning by Lemma 1.1 (IDEAL3), via the batched numpy propagation of cnt.py. paircensus.py (pure python, ~11 min for
# P112, ~7 min for P104) is the original and is what the recorded logs came from; here the numpy propagation is validated against cert2.propagate
# on 4000 random pairs and the totals are asserted against the recorded paircensus.py totals (P112 42235/diag 8, P104 45551/diag 16).
# usage: pairs_fast.py UNIT
import sys, pickle, time, random, numpy as np
from setup9 import *
unit = sys.argv[1]
L, v, G, frames, nbar, h, basis, cls = load(unit)
FR = np.array([[F >> t & 1 for t in range(v)] for F in frames], dtype=np.float32)
NB = np.array([[nbar[t] >> s & 1 for s in range(v)] for t in range(v)], dtype=np.float32)
def minS(Xs):
    S = FR[None, :, :] * (~Xs)[:, None, :]
    while True:
        Wg = ((S @ NB) > 0).all(axis=1)
        S2 = S * Wg[:, None, :]
        if np.array_equal(S2, S): break
        S = S2
    return S.sum(axis=2).min(axis=1).astype(int)
def tobits(x): return np.array([x >> t & 1 for t in range(v)], dtype=bool)
keys = sorted(cls)
random.seed(11)
smp = [cls[random.choice(keys)] & cls[random.choice(keys)] for _ in range(4000)]
ref = [min(pc(s) for s in propagate(x, frames, nbar, v)) for x in smp]
assert list(minS(np.array([tobits(x) for x in smp]))) == ref, 'numpy minS disagrees with cert2.propagate'
print('validation ok (4000 random class pairs agree with cert2.propagate)', flush=True)
pairs = [(a, b) for a in keys for b in keys if b >= a]
t0 = time.time(); unc = []; BS = 512
for i in range(0, len(pairs), BS):
    J = pairs[i:i + BS]
    m = minS(np.array([tobits(cls[a] & cls[b]) for a, b in J]))
    unc += [p for p, x in zip(J, m) if x > 0]
exp = {'P112': (42235, 8), 'P104': (45551, 16)}[unit]
got = (len(unc), sum(1 for a, b in unc if a == b))
print(unit, 'h', h, 'frames', len(frames), 'classes', len(cls), 'uncertified pairs (z<=z\')', got[0], 'diag', got[1], 'time', round(time.time() - t0), flush=True)
assert got == exp, ('mismatch with recorded paircensus.py totals', got, exp)
pickle.dump({'h': h, 'basis': basis, 'cls': cls, 'unc': unc}, open(f'pairs_{unit}.pkl', 'wb'))
