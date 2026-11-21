"""SEPPAYS test_f2.py: GF(2) pinned runs (gen.py) on small Q; exact F2 decoder mass vs R; tensor sanity R >= rank."""
import sys, random, collections
from gen import *
from fa import gfa
from f2mass import all_mass, rankQ
F = Field(2)
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
N = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
rng = random.Random(seed)
for n, P in [(3, [1, 2, 7]), (3, [1, 2, 4, 7]), (4, [1, 2, 7, 11, 13])]:
    odd, idx, dist = all_mass(P)
    st = collections.Counter(); worst = None
    for it in range(N):
        g = gen(n, P, F, rng, nh=rng.choice([1, 2, 3]), no=rng.choice([1, 2, 3]), LF=rng.choice([10, 20, 40]), p_up=rng.choice([0.03, 0.08, 0.15]))
        if g is None: st['abort'] += 1; continue
        R, meta = g
        if R.bad: st['illegal'] += 1; continue
        if R.pinned(): st['unpinned'] += 1; continue
        R2 = replay(n, P, F, meta, R.ops)
        assert not R2.bad and R2.cost == R.cost and R2.reg == R.reg
        Rec = R.rec(); pat = sum(1 << i for i, (t, s) in enumerate(odd) if Rec[t][s])
        m = dist[pat]; rk = rankQ(P, odd, pat)
        fa = gfa(n, P, F, meta, R.ops)
        st['ok'] += 1
        st['idfail'] += fa['idfail'] > 0; st['oddfail'] += fa['oddfail'] > 0
        st['rank>R (THEOREM VIOLATION)'] += rk > R.cost
        st['mass>R (LOUD)'] += m > R.cost
        st['hot-runs'] += fa['hot'] > 0
        st['FApsum>R'] += fa['psum'] > R.cost
        st['mass>rank'] += m > rk
        st['tight R==mass>0'] += R.cost == m and m > 0
        if m > R.cost: print('LOUD candidate', P, R.cost, m, rk, R.ops)
        if m > 0 and (worst is None or R.cost - m < worst[0]): worst = (R.cost - m, R.cost, m, rk, fa['hot'], fa['psum'])
    print(P, dict(st), 'min slack (R-mass, R, mass, rank, hot, FApsum)', worst, flush=True)
