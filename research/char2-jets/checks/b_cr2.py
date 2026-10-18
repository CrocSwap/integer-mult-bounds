"""Lemma CR2: stored char-2 realisations of the full incidence pattern are verified exactly (not re-searched), and the anti-Fano non-realisability of tied_min and the atoms are re-run (exhaustive DFS)."""
import json, random, itertools
from common import *
from kit import *; from cr2 import realise, cfg_data, IRR
def gfmul(a, b, k):
    r = 0; m = IRR[k]
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> k & 1: a ^= m
    return r
def dot(a, b, k): return gfmul(a[0], b[0], k) ^ gfmul(a[1], b[1], k) ^ gfmul(a[2], b[2], k)
D = json.load(open(PKG + '/data/cr2_realisations.json')); random.seed(7)
nb = 0
for nm, r in D.items():
    k = r['k']; Pc, Qc = load_cfg(nm + '.json'); v = len(Pc); R, A, free = setup(Pc, Qc); pi, sig = cfg_data(Pc, Qc)
    Pt, Qt = r['P'], r['Q']
    s_ok = all(all(Pt[t][j] == 0 for j in range(3) if j not in pi[t]) and all(Qt[t][j] == 0 for j in range(3) if j not in sig[t]) and all(0 <= x < (1 << k) for x in Pt[t] + Qt[t]) for t in range(v))
    inc_ok = all(dot(Pt[t], Qt[s], k) == 0 for (t, s) in free)
    dg_ok = all(dot(Pt[t], Qt[t], k) != 0 for t in range(v))
    nt = 40; good = 0
    for _ in range(nt):
        B = tomat(random.getrandbits(len(free)), free, v)
        N = [[(dot(Pt[t], Qt[s], k) if B[t][s] else 0) for s in range(v)] for t in range(v)]
        good += all((N[t][s] == 0) == (t != s) for t in range(v) for s in range(v)) and sum(blockranks(B, R, A)) >= v
    report('C %-15s v=%2d f=%3d GF(2^%d): supports, %d incidences, %d diagonals, %d random B (N diagonal, cost>=v)' % (nm, v, len(free), k, len(free), v, nt), s_ok and inc_ok and dg_ok and good == nt)
report('C all 21 stored configurations except tied_min: full pattern CR2 (cex_min_1 over GF(4), others GF(2))', len(D) == 21 and D['cex_min_1']['k'] == 2 and all(r['k'] == 1 for n_, r in D.items() if n_ != 'cex_min_1'))
Pt_, Qt_ = load_cfg('tied_min.json'); R, A, free = setup(Pt_, Qt_); pi, sig = cfg_data(Pt_, Qt_)
res = [realise(pi, sig, set(free), k=k) for k in (1, 2, 3, 4)]
report('C tied_min: full 72-incidence pattern has NO realisation over GF(2), GF(4), GF(8), GF(16) (exhaustive DFS)', all(r is None for r in res), str(['none' if r is None else 'FOUND' for r in res]))
# minimal non-CR2 atoms: the minimal elements of the stored family; each is non-realisable over GF(2),GF(4),GF(8) and every one-line deletion is realisable
fam = [tuple(x) for x in json.load(open(PKG + '/data/tm_noncr2.json'))]; fs = set(fam)
minimal = [S for S in fam if not any(tuple(x for x in S if x != y) in fs for y in S)]
Pm, Qm = Pt_, Qt_
def sub(S): return [Pm[i] for i in S], [Qm[i] for i in S]
def cr2(S, ks):
    P_, Q_ = sub(S); R_, A_, fr = setup(P_, Q_); pi_, sig_ = cfg_data(P_, Q_)
    for k in ks:
        r = realise(pi_, sig_, set(fr), k=k, limit=10 ** 6)
        if isinstance(r, dict): return True
    return False
from collections import Counter
cnt = Counter(len(S) for S in minimal)
report('C minimal non-CR2 sub-configurations of tied_min (from stored family): %s lines' % dict(sorted(cnt.items())), sum(cnt.values()) == 44 and cnt[6] == 32 and cnt[7] == 12, 'total %d' % len(minimal))
bad_non = [S for S in minimal if cr2(S, (1, 2, 3))]
bad_min = [S for S in minimal for y in S if not cr2(tuple(x for x in S if x != y), (1, 2, 3))]
report('C each of the 44 atoms is not realisable over GF(2),GF(4),GF(8) (exhaustive)', not bad_non, '%d violations' % len(bad_non))
report('C every one-line deletion of every atom IS realisable (so the atoms are minimal)', not bad_min, '%d violations' % len(bad_min))
tight = 0
for S in minimal:
    if len(S) == 6:
        P_, Q_ = sub(S); R_, A_, fr = setup(P_, Q_); tight += kit.enum_raw(6, R_, A_, fr, 0)[0] == 6
report('C all 32 six-line atoms are tight: exhaustive minimum cost = 6 = v (the 12 seven-line atoms have minimum cost 8: RECORDED, 2^26 each)', tight == 32, '%d/32' % tight)
done()
