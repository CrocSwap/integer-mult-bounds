import json, sys, collections, time, pickle, itertools, math
from array import array
from fractions import Fraction as Fr
from math import lcm, gcd
exec(open(sys.argv[5]).read().split("res = collections.Counter(); fdims")[0])  # chrono2 setup at CUT: cls, ff, fj, classify, nullspace, gramdet, prim
from decimal import Decimal as Dc, getcontext
getcontext().prec = 50
rep = json.load(open(sys.argv[6]))
H = {int(k): 40*v for k, v in rep['histogram'].items()}
for r in (4, 23, 46, 50): H[r] = H.get(r, 0) + 16*1760
exec(open(sys.argv[7]).read().split("print('baseline:')")[0].split("rep = json.load")[0].replace("import json, sys", ""))  # moment/price defs? simpler: redefine
LN = {}
def moment(H, W, a, m=120):
    s = Dc(0); N = 0
    for r, n in H.items():
        if n == 0: continue
        if r not in LN: LN[r] = (Dc(m)/Dc(r)).ln()
        s += Dc(r*n)/(Dc(m)*W) * (LN[r]*a).exp(); N += n
    if 'm' not in LN: LN['m'] = Dc(m).ln()
    return s + Dc(32*m*m*N)/(Dc(m)*W) * (LN['m']*a).exp() / Dc(10)**16
grid = Dc(10)**18
def price(H, W):
    lo, hi = Dc('0.0005'), Dc('0.001'); assert moment(H, W, lo) < 1 < moment(H, W, hi)
    for _ in range(80):
        mid = (lo+hi)/2
        if moment(H, W, mid) < 1: lo = mid
        else: hi = mid
    z = int(lo*grid); assert moment(H, W, Dc(z)/grid) < 1 and moment(H, W, Dc(z+1)/grid) > 1
    c = Dc(z)/grid; bit = Dc(384599)/Dc(10)**10
    for _ in range(3): bit = (1-c)*c + c*bit
    eta = Dc(1)/Dc(10)**12; q = bit*(1-2*eta); bound = (1-eta)*q/(1+q)
    return Dc(int(bound*grid))/grid
kn = price(H, Dc(173839)); print('PR254 kappa reproduced', kn)
phi = lambda r: 0.0 if r == 0 else r*math.log(120/r)
def best(ra, rb, d):
    # pivot p starts at E (dim e<=d), partner b raised to E; gain = phi(rp-e)-phi(rp) + phi(e)+phi(rb-e)-phi(rb)   (negative = good)
    out = None
    for rp, rq in ((ra, rb), (rb, ra)):
        for e in range(1, d+1):
            g = phi(rp-e)-phi(rp) + phi(e)+phi(rq-e)-phi(rq)
            if out is None or g < out[0]: out = (g, e, rp, rq)
    return out
def inter_dim_nondeg(frames):
    rows = []
    for f in frames: rows += fj[str(f)]['A']
    basis, free = nullspace(rows); d = len(basis)
    if d == 0: return 0, False
    return d, gramdet(basis) != 0
pairs = [tuple(sorted(m)) for m in cls.values() if len(m) == 2]
tab = collections.Counter(); gains = []; H2 = dict(H); W2 = Dc(173839); npos = 0; totgain = 0.0
strict_e1 = 0
for a, b in pairs:
    ra, rb = fj[str(ff[a])]['dim'], fj[str(ff[b])]['dim']
    d, nd = inter_dim_nondeg([ff[a], ff[b]])
    key = (tuple(sorted((ra, rb))), d, nd); tab[key] += 1
    if d == 0 or not nd: continue
    g, e, rp, rq = best(ra, rb, d)
    gains.append((g, e, rp, rq, a, b))
    if g < 0:
        npos += 1; totgain += g
        for r, dn in ((rp, -40), (rq, -40), (rp-e, 40), (e, 40), (rq-e, 40)):
            if r > 0: H2[r] = H2.get(r, 0) + dn
        W2 -= Dc(e)/3
print('cross-tab (sorted first-frame dims, intersection dim, nondegenerate) -> count:'); [print('  ', k, c) for k, c in sorted(tab.items(), key=lambda x: -x[1])]
print('pairs with nonzero nondegenerate intersection:', len(gains), ' of which net-positive (log-weighted) with best pivot/e:', npos, ' total phi-gain', round(totgain, 1))
print('gain histogram (e, frames) for positive pairs:', collections.Counter((e, (rp, rq)) for g, e, rp, rq, a, b in gains if g < 0).most_common(12))
k2 = price(H2, W2); print(f'price: all net-positive pairs at cut {CUT} (single cut, e<=dim): kappa={k2} dk vs PR254={k2-kn} ({float((k2-kn)/kn*100):.4f}%)  W2={W2} mass={sum(r*n for r,n in H2.items())} deficit={120*W2-sum(r*n for r,n in H2.items())}')
# restricted variant: e=1 only, nondegenerate line, any u (needs norm-2 charts)
H3 = dict(H); W3 = Dc(173839); n3 = 0
for g, e, rp, rq, a, b in gains:
    g1 = min(phi(rp-1)-phi(rp)+phi(1)+phi(rq-1)-phi(rq), phi(rq-1)-phi(rq)+phi(1)+phi(rp-1)-phi(rp))
    if g1 < 0:
        n3 += 1
        for r, dn in ((rp, -40), (rq, -40), (rp-1, 40), (1, 40), (rq-1, 40)):
            if r > 0: H3[r] = H3.get(r, 0) + dn
        W3 -= Dc(1)/3
k3 = price(H3, W3); print(f'price: e=1 only, {n3} net-positive pairs: kappa={k3} dk vs PR254={k3-kn}')
# the PR's own 132 (3,3) pairs: phi gain check
print('phi gain per (3,3) e=1 pair', round(best(3,3,1)[0],3), ' (2,2) e=1', round(best(2,2,1)[0],3), ' (2,2) e=2', round(best(2,2,2)[0],3), ' (1,1) e=1', round(best(1,1,1)[0],3), ' (5,5) e=1', round(best(5,5,1)[0],3), ' (5,5) e=3', round(best(5,5,3)[0],3), ' (3,3,3) triple e=1', round(2*(phi(1)+phi(2)-phi(3)) + phi(2)-phi(3),3))
