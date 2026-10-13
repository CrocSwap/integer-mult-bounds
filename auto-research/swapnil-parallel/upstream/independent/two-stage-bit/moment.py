"""Exact certifier for the batched two-stage bit moment.
Children per role, from the label chains of notes/two-stage-construction.tex:
  side aux role   : ranks sum to m, one edge of rank m-h (stage-1 exit D1->F or stage-2 entrance 0->D0)
  centre aux role : ranks sum to m+2h (central return h counted, plus one extra up-edge h), one edge m-h
  data role X / Y : U_a -> ... -> F and 0 -> ... -> U_a^perp, ranks h-1, h-1, m-2h+1, sum m-1
  copy correction : one rank-one child per data pair
Batching (partial-swap lemma): an edge of rank r > m/2 becomes (m-r) singletons + one block of width 2r-m.
Condition: (1/W) * sum_children (width/m)^(1-a) < 1."""
import sys
from fractions import Fraction as Q
from math import comb, log

def R_of(h):
    # side roles per invocation from our generator (additions + outputs)
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from sidegen import roles
    return roles(h)[0]

def ln_upper(x):
    """Rigorous rational upper bound of ln x for rational x > 1: ln x = k ln2 + ln y, y in (1,2];
    ln y = 2 atanh z, z=(y-1)/(y+1) <= 1/3; partial sum + geometric tail bound."""
    x = Q(x); assert x > 1
    k = 0
    while x > 2: x /= 2; k += 1
    def two_atanh_up(z, n=30):
        s = sum(z**(2*j+1)/(2*j+1) for j in range(n))
        tail = z**(2*n+1)/((2*n+1)*(1-z*z))
        return 2*(s+tail)
    return k*two_atanh_up(Q(1, 3)) + (two_atanh_up((x-1)/(x+1)) if x > 1 else 0)

def histogram(h, R, data_batch):
    """Exact multiset {width: count} of children, built role by role (not from s)."""
    v, m, c0 = comb(h, 3), h*h, h; N = v*v
    hist = {}
    def add(w, c): hist[w] = hist.get(w, 0)+c
    def edge(r, cnt, batch):
        if batch and 2*r > m: add(1, (m-r)*cnt); add(2*r-m, cnt)
        else: add(1, r*cnt)
    A = v*(R+c0)                    # aux roles per stage (v invocations, R side + c0 centre each)
    for _stage in range(2):
        edge(m-h, A, True)                                  # the selected aux edge
        edge(h, v*R, False)                                 # rest of each side role: m-(m-h)
        edge(3*h, v*c0, False)                              # rest of each centre role: m+2h-(m-h)
    # data: two roles per pair; stage-2 entrance m-2h+1 plus two edges of h-1
    edge(m-2*h+1, 2*N, data_batch); edge(2*(h-1), 2*N, False)
    add(1, N)                                               # copy correction
    W = 2*N+2*A; L = 2*v*h*c0
    s = sum(w*c for w, c in hist.items())
    assert s == W*m-N+2*L, 'rank sum mismatch'
    assert W*m-s == v*(v-4*h*c0)
    return dict(h=h, m=m, v=v, N=N, W=W, L=L, s=s, R=R, hist=hist)

def F_upper(c, a, lu):
    m, W = c['m'], c['W']; tot = Q(0)
    for w, cnt in c['hist'].items():
        # (w/m)^(1-a) = (w/m) * (m/w)^a <= (w/m) / (1 - a ln(m/w))
        l = lu[w]; assert a*l < 1
        tot += Q(cnt*w, m)/(1-a*l)
    return tot/W

def F_float(c, a):
    m, W = c['m'], c['W']
    return sum(cnt*(w/m)**(1-a) for w, cnt in c['hist'].items())/W

def certify(c, den=10**9):
    lo, hi = 0.0, 0.05
    for _ in range(200):
        mid = (lo+hi)/2
        lo, hi = (mid, hi) if F_float(c, mid) < 1 else (lo, mid)
    lu = {w: ln_upper(Q(c['m'], w)) for w in c['hist']}
    n = int(lo*den)+1
    while not F_upper(c, Q(n, den), lu) < 1: n -= 1
    assert F_upper(c, Q(n, den), lu) < 1
    return Q(n, den), lo

if __name__ == '__main__':
    assert ln_upper(1024) > Q(6931471805599453, 10**15) and ln_upper(1024) < Q(6931471805599454, 10**15)
    for arg in sys.argv[1:]:
        h, db = arg.split(':'); h = int(h); db = db == '1'
        c = histogram(h, R_of(h), db); a, root = certify(c)
        print('h=%d data_batch=%d v=%d m=%d R=%d N=%d W=%d L=%d s=%d  a_b=%s (=%.6e) root %.6e  hist=%s'
              % (h, db, c['v'], c['m'], c['R'], c['N'], c['W'], c['L'], c['s'], a, float(a), root,
                 sorted(c['hist'].items())), flush=True)
