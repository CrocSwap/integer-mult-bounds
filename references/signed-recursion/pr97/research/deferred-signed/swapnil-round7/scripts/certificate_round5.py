"""Round-five witness: our stack with the two-stage bit interchange in the common flag basis
(notes/flag-basis.tex) and the global-matching side circuit (independent/two-stage-bit/gmside.py), and PR #7's
complex network fully batched with complex source frames (h=28).

Usage: python3 scripts/certificate_round5.py COMPLEX_HIST_JSON
where the JSON comes from independent/complex-network/fullbatch_hist.py 28 OUT sf."""
import sys, math, os
from fractions import Fraction as Q
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'independent', 'two-stage-bit'))
from certificate_round3 import evaluate
from certificate_round4 import complex_saving
import moment, gmside, side_chains
from collections import Counter

BIT_H = 47

def side_ranks(h):
    # factor ranks of every side-role edge (stage one; stage two has the same idempotents in reverse order)
    G = side_chains.build(h, side_chains.ORDERS['gm']); C = side_chains.compile_(G); rk = Counter()
    for s in range(C['roles']):
        d = side_chains.chain_dims(G, C, s)
        for a, b in zip(d, d[1:]): rk[b - a] += 1
    return C['roles'], rk

def inner_children(r, h):
    # inner lemma: an edge pi (x) P_b with rank pi = r has the profile of a rank-r idempotent of size h
    return [1] * (h - r) + [2*r - h] if 2*r > h else [1] * r

def flag_histogram(h, R, side=None):
    # children per role under the flag basis (Proposition "Profiles"):
    #   selected aux edge, both stages: one block m-2h and one run h (corners merged)
    #   rest of each side role: h singletons (not batched here)
    #   centre roles: their three rank-h edges are one run each
    #   data: entrance block m-4h+2, corner run h-2 and h+1 singletons; the two (h-1)-edges are a block h-2 plus a singleton
    #   copy correction: one singleton per pair
    v, m, c0 = comb(h, 3), h*h, h; N = v*v; A = v*(R+c0); H = {}
    add = lambda w, c: H.__setitem__(w, H.get(w, 0) + c)
    for _ in range(2):
        add(m-2*h, A); add(h, A)
        if side is None: add(1, h*v*R)
        else:
            assert sum(r*n for r, n in side.items()) == h*R, 'side ranks sum to h per role'
            for r, n in side.items():
                for w in inner_children(r, h): add(w, v*n)
        add(h, 3*v*c0)
    add(m-4*h+2, 2*N); add(h-2, 2*N); add(1, (h+1)*2*N)   # entrance corner: one run h-2 (rank-one term on a triangular corner)
    for _ in range(2):
        add(h-2, 2*N); add(1, 2*N)
    add(1, N)
    W = 2*N + 2*A; L = 2*v*h*c0; s = W*m - N + 2*L
    assert sum(w*n for w, n in H.items()) == s and W*m > s
    return dict(h=h, m=m, v=v, N=N, W=W, L=L, s=s, R=R, hist=H)

def bit_saving(side=True):
    if side:
        R, rk = side_ranks(BIT_H)
        assert R == gmside.roles(BIT_H)[0]
    else:
        R, rk = gmside.roles(BIT_H)[0], None
    c = flag_histogram(BIT_H, R, rk)
    a, _ = moment.certify(c)
    return a, c

if __name__ == '__main__':
    ac, cc = complex_saving(sys.argv[1])
    ab, cb = bit_saving()
    print('a_b', ab, '(h=%d, R=%d)' % (BIT_H, cb['R']))
    print('a_c', ac, '(h=%d, R=%d, s=%d)' % (cc['h'], cc['R'], cc['s']))
    r = evaluate(ab, ac, Q(1, 1000), 'crude', m_c=cc['m'], s_c=cc['s'])
    print('crude guard: ok=%s kappa=%s (%.6e, 2^%.3f) binding=%s %s' % (
        r['ok'], r['kappa'], r['kappa'], math.log2(r['kappa']), r['binding'], r['bad']))
