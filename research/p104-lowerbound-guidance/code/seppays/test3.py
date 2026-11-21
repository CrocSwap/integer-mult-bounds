"""SEPPAYS test3.py: gen3 separation gadgets; CT theorem check (per-group price <= cost, decoder identity) and exact mass."""
import sys, random, collections
from gen3 import gen3
from eng import *
from sepcheck import analyse
from fa import eff, price
from f2mass import all_mass, rankQ
p = int(sys.argv[1]); seed = int(sys.argv[2]); N = int(sys.argv[3]); VARS = sys.argv[4].split(',') if len(sys.argv) > 4 else ['tree', 'shared', 'pub']
F = Field(p); rng = random.Random(seed)
for n, P in [(3, [1, 2, 4, 7]), (4, [1, 2, 7, 11, 13])]:
    if p == 2: odd, idx, dist = all_mass(P)
    for variant in VARS:
        st = collections.Counter()
        for it in range(N):
            R, meta = gen3(n, P, F, rng, nh=rng.choice([1, 2]), ngad=rng.choice([1, 2, 3, 4]), variant=variant)
            if R.bad: st['illegal'] += 1; continue
            if R.pinned(): st['unpinned'] += 1; continue
            a = analyse(n, P, F, meta, R.ops)
            st['ok'] += 1; st['FA idfail'] += a['fa']['idfail'] > 0; st['FA oddfail'] += a['fa']['oddfail'] > 0
            st['hot'] += a['fa']['hot'] > 0
            inCT = a['gtd'] and a['forest'] and all(g['cold'] for g in a['groups'])
            st['in CT'] += inCT
            if inCT:
                st['CT viol (price>cost)'] += any(g['price'] > g['cost'] for g in a['groups'])
                st['CT hot & in class'] += a['fa']['hot'] > 0
                st['CT sum>R'] += sum(g['price'] for g in a['groups']) > R.cost
            Rec = R.rec(); T = len(P)
            if p == 2:
                pat = sum(1 << i for i, (t, s) in enumerate(odd) if Rec[t][s]); m = dist[pat]
                st['mass>R LOUD'] += m > R.cost; st['nontriv'] += m > 0; st['tight'] += (m == R.cost and m > 0)
                if m > R.cost: print('LOUD', variant, P, R.cost, m, R.ops, flush=True)
            else:
                nzr = sum(any(Rec[t][s] != 0 and dot(P[t], P[s]) for s in range(T)) for t in range(T))
                nzc = sum(any(Rec[t][s] != 0 and dot(P[t], P[s]) for t in range(T)) for s in range(T))
                ctsum = sum(g['price'] for g in a['groups']) if inCT else 99
                best = min(a['fa']['psum'], nzr, nzc, ctsum)
                st['unresolved'] += best > R.cost; st['FA>R'] += a['fa']['psum'] > R.cost
        print('F' + str(p), P, variant, dict(st), flush=True)
