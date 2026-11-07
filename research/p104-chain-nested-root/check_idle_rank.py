#!/usr/bin/env python3
"""Standalone (stdlib) check for the #6833 whole-idle rank addendum.
Decimal arithmetic at 60 digits (diagnostic, not interval-certified; the package's
own interval engines certify the same quantities). Histograms are #6833's RESULT.json."""
from decimal import Decimal as D, getcontext
import random
getcontext().prec = 60
T = {1:356,2:144,3:72,4:1962,5:306,6:54,7:180,8:720,9:6670,17:208,25:208,33:208,41:208,
     49:208,57:208,65:208,73:208,145:104}
P = {1:40524,2:8172,3:8802,4:1980,5:2736,6:126,7:162,8:226,16:208,24:208,32:208,
     40:208,48:208,56:208,64:208}
TESTED, KAPPA = D('0.00337180035'), D('0.0033718')
OFF, CUT, FLOOR, DECAY, RESERVE = D(1)/D(7), 11, 12, D(31)/D(32), D(10)**-27
ok = True
def need(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m); ok &= bool(c)
mom = lambda H, s: sum(D(n)*D(r)**s for r, n in H.items())
def tails(Pp, t=1-TESTED):
    tt = mom(T, t)
    return (mom(Pp, t)/tt, mom(Pp, t+OFF)/(D(CUT)**OFF*tt),
            D(sum(T.values())*FLOOR)/(D(CUT)**TESTED*tt))
def root(Pp):
    lo, hi = D('0.002'), D('0.0034')
    for _ in range(150):
        m = (lo+hi)/2
        if mom(T, 1-m) - mom(Pp, 1-m) > 0: lo = m
        else: hi = m
    return lo

need(sum(r*n for r, n in T.items()) - sum(r*n for r, n in P.items()) == 760, 'rank-mass surplus 760')
need(max(P) == 64 and max(T) == 145 and sum(P.values()) == 64184, 'max paid 64, max target 145, 64184 paid')
need(sum(r*n for r, n in P.items()) == 166812, 'paid rank mass 166812')
k0 = root(P); print('raw crossing', str(k0)[:16])
need(D('0.0033718004754') < k0 < D('0.0033718004755'), 'raw crossing in package interval')
need(KAPPA < TESTED < k0, 'claim < tested < crossing')
al, ga, de = tails(P)
print('alpha 1-%.3e gamma %.6f delta %.6f' % (1-al, ga, de))
need(al < 1-RESERVE and ga < DECAY and de < DECAY, 'alpha, gamma, delta tails at max rank 64')
# Rank-free integer constants (no paid rank appears)
need(CUT**64 < FLOOR**63, '11^64 < 12^63')
need(2*(CUT**1920)**64 <= (145**1920)**63, '2*(11^p)^64 <= (145^p)^63, m=max TARGET 145')
# Direction of rank dependence. alpha uses exponent t<1 (concave: merging idles LOWERS it).
# gamma uses exponent t+u>1 (CONVEX: merging idles RAISES it). Rank enters only through these.
t = 1-TESTED
need(t < 1 < t+OFF, 'exponents: t<1 (alpha), t+u>1 (gamma)')
need(D(64)**t < 8*D(8)**t, 'alpha: merged rank 64 moment < eight rank-8 fragments')
need(D(64)**(t+OFF) > 8*D(8)**(t+OFF), 'gamma: merged rank 64 moment > eight rank-8 fragments (rank-sensitive)')
# Sensitivity: replace the 208 rank-64 idles by rank-R idles, other data fixed
def with_idle(R):
    Q = dict(P); n = Q.pop(64); Q[R] = Q.get(R, 0)+n; return Q
def bisect(f, lo, hi):
    for _ in range(100):
        m = (lo+hi)/2
        if f(m): lo = m
        else: hi = m
    return lo
Rstar = bisect(lambda R: tails(with_idle(int(R)))[1] < DECAY, 64, 20000)
print('gamma (u=1/7) first fails when the 208 rank-64 idles become rank R ~', int(Rstar))
for R in (40, 64, 72, 144):
    print(' R=%3d gamma %.6f' % (R, tails(with_idle(R))[1]))
need(Rstar >= 72, 'rank-64 -> 72 still passes gamma at the pinned u=1/7 (headroom factor %.3f)' % (Rstar/64))
need(tails(with_idle(144))[1] > DECAY, 'documented limit: 208 whole idles of rank 144 would FAIL gamma at u=1/7')
# u is a free proof parameter of the strictification theorem (sigma=t+u>=1 only); compiler grid is independent of u
best = min((tails(P, t)[1] if False else mom(P, t+u)/(D(CUT)**u*mom(T, t)), u) for u in
           (D(x)/100 for x in range(1, 51)))
print('best u on grid %.2f -> gamma %.6f' % (best[1], best[0]))
need(best[0] < ga, 'a better u exists (escape route if the margin were ever needed)')
Q8 = dict(P)
for r in (16,24,32,40,48,56,64): n = Q8.pop(r); Q8[8] = Q8.get(8, 0)+n*(r//8)
need(tails(Q8)[1] < ga, 'cutting idles into rank-8 pieces LOWERS gamma (and raises alpha)')
need(tails(Q8)[0] > al, 'cutting idles raises alpha (alpha still < 1 but kappa falls)')
print('kappa if all idles cut to rank 8:', str(root(Q8))[:12])
# Split-charge inequality of the strictification theorem (any R > J, sigma = t+u >= 1)
random.seed(1); bad = 0
for _ in range(20000):
    C = random.uniform(1e-3, .9); u = random.uniform(C, 2); J = random.randint(2, 500)
    R = random.randint(J+1, 50000); q, r = divmod(R, J)
    lhs = q*J**(1-C) + r**(1-C); rhs = 2*R**(1-C+u)*J**-u
    bad += lhs > rhs*(1+1e-12)
need(bad == 0, 'split charge q J^t + r^t <= 2 R^(t+u) J^-u on 20000 samples (sigma>=1)')
print('ALL PASS' if ok else 'FAILURES')
raise SystemExit(0 if ok else 1)
