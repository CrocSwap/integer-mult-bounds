"""Exact batched moment for the two-stage bit network (independent of batched_two_stage.py).
Psi(1-a) = sum_i w_i exp(a log(1/r_i)) <= sum_i w_i/(1 - a l_i), l_i rigorous rational upper bounds."""
from fractions import Fraction as Q
from math import comb, log

def log_ub(x, terms=40):
    """Rigorous upper bound for log x, x>1 rational: 2*sum z^(2j+1)/(2j+1) + tail, z=(x-1)/(x+1)."""
    x = Q(x); k = 0
    while x > 2: x /= 2; k += 1          # extract powers of two
    def at(z):
        s = sum(2*z**(2*j+1)/(2*j+1) for j in range(terms))
        return s + 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    return k*at(Q(1, 3)) + (at((x-1)/(x+1)) if x > 1 else 0)

def classes(h, R, data):
    v, m, c0 = comb(h, 3), h*h, h
    N = v*v; W = 2*N+2*v*(R+c0); L = 2*v*h*c0; s = W*m-N+2*L
    cl = [(2*v*(R+c0), m-2*h)]                         # aux: rank m-h -> h corners + block t=m-2h
    if data == 'correct': cl.append((2*N, m-4*h+2))    # stage-2 data entrances: rank m-2h+1 -> t=m-4h+2
    if data == 'as-script': cl.append((2*N, m-2*h))
    return dict(m=m, W=W, s=s, cl=cl)

def bound(c, a):
    m, W, s = c['m'], c['W'], c['s']
    single = s-sum(B*t for B, t in c['cl'])
    tot = Q(single, W*m)/(1-a*log_ub(m))
    for B, t in c['cl']: tot += Q(B*t, W*m)/(1-a*log_ub(Q(m, t)))
    return tot

def true_root(c):
    m, W, s = c['m'], c['W'], c['s']; single = s-sum(B*t for B, t in c['cl'])
    f = lambda a: single/(W*m)*m**a + sum(B*t/(W*m)*(m/t)**a for B, t in c['cl'])
    lo, hi = 0.0, 1e-3
    for _ in range(200):
        mid = (lo+hi)/2; lo, hi = (mid, hi) if f(mid) < 1 else (lo, mid)
    return lo

if __name__ == '__main__':
    assert log_ub(1024) > Q(6931471805599453, 10**15)
    for data in ('none', 'correct', 'as-script'):
        c = classes(32, 123157, data)
        claim = Q(22157, 5*10**9)
        b = bound(c, claim)
        print('data=%-9s claimed a_b=%s: certified bound %.12f <1: %s, gap %.3e; true root a*=%.6e'
              % (data, claim, float(b), b < 1, float(1-b), true_root(c)))
        n = int(true_root(c)*10**10)+2
        while not bound(c, Q(n, 10**10)) < 1: n -= 1
        print('    largest certified a at 1e-10 grid: %s = %.4e' % (Q(n, 10**10), n/1e10))
