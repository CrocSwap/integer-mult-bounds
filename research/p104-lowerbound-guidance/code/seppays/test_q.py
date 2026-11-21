"""SEPPAYS test_q.py: Q pinned runs (gen2); decoders: FA rows, per-row, per-column; flag runs where none has price <= R."""
import sys, random, collections, pickle
from gen2 import gen2
from eng import *
from fa import gfa
seed = int(sys.argv[1]); N = int(sys.argv[2])
F = Field(0); rng = random.Random(seed)
unres = []
for n, P in [(3, [1, 2, 7]), (3, [1, 2, 4, 7]), (4, [1, 2, 7, 11, 13]), (4, [1, 2, 4, 8, 7, 11, 13, 14])]:
    st = collections.Counter(); T = len(P)
    for it in range(N):
        R, meta = gen2(n, P, F, rng, nh=rng.choice([1, 2, 3]), no=rng.choice([1, 2, 3]), LF=rng.choice([15, 30, 60]), p_up=rng.choice([0.03, 0.08, 0.15]))
        if R.bad or R.pinned(): st['bad'] += 1; continue
        fa = gfa(n, P, F, meta, R.ops)
        st['ok'] += 1; st['idfail'] += fa['idfail'] > 0; st['oddfail'] += fa['oddfail'] > 0; st['hot'] += fa['hot'] > 0
        Rec = R.rec()
        nzr = sum(any(Rec[t][s] != 0 and dot(P[t], P[s]) for s in range(T)) for t in range(T))
        nzc = sum(any(Rec[t][s] != 0 and dot(P[t], P[s]) for t in range(T)) for s in range(T))
        best = min(fa['psum'], nzr, nzc)
        st['FA>R'] += fa['psum'] > R.cost
        if best > R.cost:
            st['UNRESOLVED'] += 1; unres.append((n, P, meta, R.ops, R.cost, best, Rec))
    print(P, dict(st), flush=True)
pickle.dump(unres, open(f'q_unres_{seed}.pkl', 'wb'))
print('unresolved', len(unres))
for u in unres[:10]: print('  R', u[4], 'best decoder', u[5], 'P', u[1])
