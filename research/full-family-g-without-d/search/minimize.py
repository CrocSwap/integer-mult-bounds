"""Replay walk(seed) to its first full-family G-pass D-fail step, then greedily restore deleted lines while the
criterion verdict stays 'D' (W, blocks, G pass; D fails mod p). Output locally minimal deletion sets."""
import os
import json, random, sys, collections
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.environ['PR1650_PACKAGE'])  # research/complex-rank8-rigidity-p105 at PR1650 head d960f8a2
import verify as V
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walk import PIVOTS

def first_dev(seed):
    rng = random.Random(seed)
    p = rng.choice(PIVOTS); F = V.FRAMES[p]
    X = []
    cand = [i for i in V.P112 if i not in F]
    rng.shuffle(cand)
    for i in cand:
        r = V.criterion(tuple(X + [i]), F)[0]
        if r in ('W', 'nonempty-blocks'):
            continue
        X.append(i)
        if r == 'D':
            return p, X
    return None

def minimize(seed):
    fd = first_dev(seed)
    if not fd: return None
    p, X = fd; F = V.FRAMES[p]
    changed = True
    while changed:
        changed = False
        for i in sorted(X, key=lambda i: random.Random(seed * 1000 + i).random()):
            Y = [j for j in X if j != i]
            if V.criterion(tuple(Y), F)[0] == 'D':
                X = Y; changed = True
    return dict(seed=seed, pivot=p, X=sorted(X), n=len(X))

if __name__ == '__main__':
    res = json.load(open(sys.argv[1]))
    seeds = [r['seed'] for r in res if r['ndev']]
    with ProcessPoolExecutor(10) as ex:
        out = [m for m in ex.map(minimize, seeds) if m]
    out.sort(key=lambda m: m['n'])
    print('minimized', len(out), 'deletion sizes', collections.Counter(m['n'] for m in out).most_common())
    print(out[:3])
    json.dump(out, open(sys.argv[2], 'w'))
