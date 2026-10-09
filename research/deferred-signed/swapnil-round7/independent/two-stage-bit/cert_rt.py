"""Certify a_b for the retained-total gm producer with copied retained centres (lever A), and the baseline
(direct centres, certificate_round6.copied_histogram) at the same h.
Usage: python3 cert_rt.py h..."""
import sys, os, json
from math import comb
import rtgm
MODE = os.environ.get('MODE', 'search'); MODE = True if MODE == 'local' else MODE
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', '..', 'scripts'), HERE]
import moment, certificate_round6 as c6
from certificate_round5 import inner_children

def rt_histogram(h, R, rk):
    v, m = comb(h, 3), h * h; N = v * v; A = v * R; H = {}
    add = lambda w, c: H.__setitem__(w, H.get(w, 0) + c) if c else None
    assert sum(r * n for r, n in rk.items()) == h * R
    for _ in range(2):
        add(m - 2 * h, A); add(h, A)                         # selected aux edge (flag basis): block + corner run
        for r, n in rk.items():
            for w in inner_children(r, h): add(w, v * n)      # side chains incl. retained slots (to U_c, then F)
        for w in inner_children(h - 1, h): add(w, v * h)      # copy of each retained total: U_c -> D0, rank h-1
    add(m - 4 * h + 2, 2 * N); add(h - 2, 2 * N); add(1, (h + 1) * 2 * N)
    for _ in range(2):
        add(h - 2, 2 * N); add(1, 2 * N)
    add(1, N)
    W = 2 * N + 2 * A; L = 2 * v * h * (h - 1); s = W * m - N + L
    assert sum(w * n for w, n in H.items()) == s and W * m > s and max(H) <= m - 1
    return dict(h=h, m=m, v=v, N=N, W=W, L=L, s=s, R=R, hist=H)

if __name__ == '__main__':
    res = {}
    for h in map(int, sys.argv[1:]):
        R, rk, C, G = rtgm.side_ranks(h, MODE)
        c = rt_histogram(h, R, rk); a, root = moment.certify(c)
        b = c6.copied_histogram(h); ab, rb = moment.certify(b)
        print('h=%d retained R=%d a_b=%s (%.6e) | direct R+h=%d a_b=%s (%.6e) | ratio %.4f' % (
            h, R, a, float(a), b['R'] + h, ab, float(ab), float(a / ab)), flush=True)
        res[h] = dict(R=R, a=str(a), s=c['s'], W=c['W'], L=c['L'], base=str(ab))
    json.dump(res, open('cert_rt_%s.json' % '_'.join(sys.argv[1:]), 'w'), indent=1)
