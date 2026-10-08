"""Round-four witness: our stack with PR #24's endpoint-gauge bit network (its published child-width
multiset, certified here by our own moment bisection) and PR #7's complex network fully batched with
complex source frames (h=28). Also reports the witness with our own two-stage bit interchange
(data edges batched, h=47).

Usage: python3 scripts/certificate_round4.py COMPLEX_HIST_JSON
where the JSON comes from independent/complex-network/fullbatch_hist.py 28 OUT sf."""
import sys, json, math, os
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'independent', 'two-stage-bit'))
sys.path.insert(0, os.path.join(HERE, '..', 'independent', 'complex-network'))
from certificate_round3 import evaluate
import moment
from fullbatch_cert import cert

BIT_H = 47

def bit_saving():
    c = moment.histogram(BIT_H, moment.R_of(BIT_H), True)
    a, _ = moment.certify(c)
    return a, c

def pr24_bit_saving():
    d = json.load(open(os.path.join(HERE, '..', 'certificates', 'external', 'pr24-bit-network.json')))
    c = d['counts']; hist = {int(w): n for w, n in d['child_width_multiplicities']}
    W, m, s = c['W'], c['m'], c['total_rank']
    assert sum(w * n for w, n in hist.items()) == s and W * m - s == c['deficit'] and max(hist) <= m - 1
    a = cert_exp(hist, W, m)
    return a, c

def cert_exp(hist, W, m, grid=10**13):
    # largest a on the grid with sum_t c_t t (m/t)^a / (W m) < 1, using U_t > ln(m/t) and
    # e^x <= 1 + x + x^2/2 + x^3 for 0 <= x <= 1/2 (the tail sum_{k>=3} x^k/k! is at most x^3)
    from bc import ln_upper
    ws = [(Q(t * n, W * m), ln_upper(Q(m, t), rel=Q(1, 10**15))) for t, n in hist.items()]
    def mom(a):
        tot = Q(0)
        for w, U in ws:
            x = a * U; assert x <= Q(1, 2)
            tot += w * (1 + x + x * x / 2 + x ** 3)
        return tot
    lo, hi = 0, 10**9
    assert mom(Q(hi, grid)) > 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mom(Q(mid, grid)) < 1: lo = mid
        else: hi = mid
    return Q(lo, grid)

def complex_saving(path):
    d = json.load(open(path)); hist = {int(k): v for k, v in d['hist'].items()}
    assert d['sum_ok'] and d['checker']['bad'] == 0 and max(hist) <= d['m'] - 1
    a, gap = cert(hist, d['W'], d['m'], d['s'])
    return a, d

if __name__ == '__main__':
    ac, cc = complex_saving(sys.argv[1])
    print('a_c', ac, '(h=%d, R=%d, s=%d)' % (cc['h'], cc['R'], cc['s']))
    ab24, c24 = pr24_bit_saving()
    ab, cb = bit_saving()
    for name, a in (('PR #24 bit network (headline)', ab24), ('our two-stage bit, h=%d' % BIT_H, ab)):
        r = evaluate(a, ac, Q(1, 1000), 'crude', m_c=cc['m'], s_c=cc['s'])
        print('%s: a_b=%s ok=%s kappa=%s (%.6e, 2^%.3f) binding=%s %s' % (
            name, a, r['ok'], r['kappa'], r['kappa'], math.log2(r['kappa']), r['binding'], r['bad']))
