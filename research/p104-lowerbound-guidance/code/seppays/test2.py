"""SEPPAYS test2.py: carrier-biased pinned runs (gen2) over GF(2) with exact F2 decoder mass, and over Q with the FA decoder."""
import sys, random, collections
from gen2 import gen2
from eng import *
from fa import gfa
from f2mass import all_mass, rankQ
p = int(sys.argv[1]); seed = int(sys.argv[2]); N = int(sys.argv[3])
F = Field(p); rng = random.Random(seed)
cases = [(3, [1, 2, 7]), (3, [1, 2, 4, 7]), (4, [1, 2, 7, 11, 13])]
for n, P in cases:
    if p == 2: odd, idx, dist = all_mass(P)
    st = collections.Counter(); slack = collections.Counter(); keep = []
    for it in range(N):
        R, meta = gen2(n, P, F, rng, nh=rng.choice([1, 2, 3]), no=rng.choice([1, 2, 3]), LF=rng.choice([15, 30, 60]), p_up=rng.choice([0.03, 0.08, 0.15]))
        if R.bad: st['illegal'] += 1; continue
        if R.pinned(): st['unpinned'] += 1; continue
        R2 = replay(n, P, F, meta, R.ops); assert not R2.bad and R2.cost == R.cost and R2.reg == R.reg
        fa = gfa(n, P, F, meta, R.ops)
        st['ok'] += 1; st['idfail'] += fa['idfail'] > 0; st['oddfail'] += fa['oddfail'] > 0
        st['hot-runs'] += fa['hot'] > 0; st['FApsum>R'] += fa['psum'] > R.cost
        if p == 2:
            Rec = R.rec(); pat = sum(1 << i for i, (t, s) in enumerate(odd) if Rec[t][s])
            m = dist[pat]; rk = rankQ(P, odd, pat)
            st['rank>R (THEOREM VIOLATION)'] += rk > R.cost; st['mass>R (LOUD)'] += m > R.cost
            st['nontrivial'] += m > 0; st['gap pattern'] += m > rk
            if m > 0: slack[R.cost - m] += 1
            if m > R.cost: print('LOUD', P, R.cost, m, rk, R.ops, flush=True)
            if fa['psum'] > R.cost: keep.append((R.cost, m, rk, fa['psum'], fa['hot']))
        else:
            if fa['psum'] > R.cost: keep.append((R.cost, fa['psum'], fa['hot'], R.ops))
    print(P, dict(st), 'slack hist', sorted(slack.items())[:6], flush=True)
    for k in keep[:5]: print('   FA>R example', k[:4] if p == 2 else k[:3])
