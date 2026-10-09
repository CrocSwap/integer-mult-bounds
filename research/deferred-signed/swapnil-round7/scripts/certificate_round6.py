"""Round-six witness, bit side: the round-five two-stage interchange (flag basis, gm side circuit, side roles batched
one level down, data-entrance run) with copied centres (PR #36's copied retained-centre schedule, here on direct centre
wires). Each centre's second scatter reads from a temporary copy moved to D0 (rank h) while the original stays at D1,
so a centre has two children of width h per stage instead of three, and the rank budget is s = Wm - N + L.
The copy is a temporary, not a role: W is unchanged; the schedule needs one extra role tape.

Usage: python3 scripts/certificate_round6.py"""
import sys, math, os
from fractions import Fraction as Q
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'independent', 'two-stage-bit'))
import certificate_round5 as c5
import moment

BIT_H = 25

def copied_histogram(h):
    R, rk = c5.side_ranks(h)
    v, m, c0 = comb(h, 3), h*h, h; N = v*v; A = v*(R+c0); H = {}
    add = lambda w, c: H.__setitem__(w, H.get(w, 0) + c) if c else None
    for _ in range(2):
        add(m-2*h, A); add(h, A)
        for r, n in rk.items():
            for w in c5.inner_children(r, h): add(w, v*n)
        add(h, 2*v*c0)                       # copied centres: two rank-h children per centre per stage
    add(m-4*h+2, 2*N); add(h-2, 2*N); add(1, (h+1)*2*N)
    for _ in range(2):
        add(h-2, 2*N); add(1, 2*N)
    add(1, N)
    W = 2*N + 2*A; L = 2*v*h*c0; s = W*m - N + L
    assert sum(w*n for w, n in H.items()) == s and W*m > s and max(H) <= m - 1
    return dict(h=h, m=m, v=v, N=N, W=W, L=L, s=s, R=R, hist=H)

def bit_saving(h=BIT_H):
    c = copied_histogram(h)
    a, _ = moment.certify(c)
    return a, c

RT_H = 23

def retained_saving(h=RT_H):
    # retained point totals replace the direct centre wires: each total's copy pays U_c -> D0 (rank h-1) and the
    # original U_c -> F (rank 1); the totals are side roles built from existing nodes (independent/two-stage-bit/rtgm.py)
    import rtgm, cert_rt
    R, rk, _, _ = rtgm.side_ranks(h, 'search')
    c = cert_rt.rt_histogram(h, R, rk)
    a, _ = moment.certify(c)
    return a, c

if __name__ == '__main__':
    a, c = retained_saving()
    print('a_b', a, float(a), '(retained totals, h=%d, R=%d, s=%d)' % (c['h'], c['R'], c['s']))
    a, c = bit_saving()
    print('a_b', a, float(a), '(h=%d, R=%d, s=%d, deficit=%d)' % (c['h'], c['R'], c['s'], c['W']*c['m'] - c['s']))
