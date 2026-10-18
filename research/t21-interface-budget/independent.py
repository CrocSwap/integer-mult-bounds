# SPDX-License-Identifier: Apache-2.0
"""Independent float cross-check of the committed budget numbers.

Shares no code with classify.py, budget.py or the pinned engines:
- role masses from endpoint ranks alone (no climb replay), using integer
  Gaussian elimination over F2 on lists rather than echelon dictionaries;
- complex/bit roots of sum p_r (m/r)^a = 1 by float Newton iteration (no
  rational enclosures), compared with the certified grid endpoints;
- kappa via the closed bootstrap form a_{k+1} = (1-s)s + s a_k.
Floats only corroborate; the rational certificates are in budget.py.

Usage: independent.py U8-FULL-WORD.json.gz RESULT-CLASSIFICATION.json RESULT-BUDGET.json
"""
import gzip
import json
import math
from fractions import Fraction
import sys
from collections import Counter


def rank2(vectors):
    rows, r = [v for v in vectors if v], 0
    for bit in range(31, -1, -1):
        piv = next((i for i in range(r, len(rows)) if rows[i] >> bit & 1), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i] >> bit & 1:
                rows[i] ^= rows[r]
        r += 1
    return r


def froot(H, m, W, bad=False):
    p = {r: r*n/(m*W) for r, n in H.items()}
    f = (32*m*sum(H.values()))/(1e16*W) if bad else 0.0
    a = 0.001
    for _ in range(60):
        g = sum(q*(m/r)**a for r, q in p.items()) + f*m**a - 1
        d = sum(q*math.log(m/r)*(m/r)**a for r, q in p.items()) + f*math.log(m)*m**a
        a -= g/d
    return a


def fkappa(c, b):
    s = min(c, (1-1e-24)*b)
    a = 0.0000384599
    for _ in range(7):
        a = (1-s)*s + s*a
    q = a*(1-2e-24)
    return (1-1e-24)*q/(1+q)


def main():
    w = json.loads(gzip.open(sys.argv[1]).read())
    cls = json.loads(open(sys.argv[2]).read())
    bud = json.loads(open(sys.argv[3]).read())
    h, v, R = w['report']['h'], w['report']['v'], w['report']['R']
    entering, low = set(map(int, w['start_extra'])), set(map(int, w['helper_final']))
    start = [rank2([p]) for p in w['ports']] + [0]*(v+R)
    for q, U in w['start_extra'].items():
        start[int(q)] = rank2(U)
    end = [h]*v + [h-1]*v + [h]*R
    for q, U in w['helper_final'].items():
        end[int(q)] = rank2(U)
    mass = Counter()
    for q in range(2*v+R):
        kind = 'source' if q < v else 'target' if q < 2*v else (
            'helper_' + ('entering' if q in entering else 'cold') + ('_lowend' if q in low else '_full'))
        mass[kind] += end[q] - start[q]
    mass['centre'] = sum(rank2(U) for U in w['center_frames'])
    assert dict(mass) == cls['mass_by_role'], (dict(mass), cls['mass_by_role'])

    claim = dict(local={1: 2548, 2: 338, 3: 446, 4: 162, 5: 72, 8: 8}, idle={48: 6292, 3: 1, 1: 3})
    glob = lambda L: Counter({**{r: 189*n for r, n in L.items() if n}}) + Counter(claim['idle'])
    bit = json.loads(open(sys.argv[4] if len(sys.argv) > 4 else
                          'research/complex-t21-owners/vendor/pr870/inputs/PR589-EXPECTED.json').read())['nine']
    c = froot({int(r): n for r, n in bit['profile'].items()}, 64, bit['bit']['live'], True)
    b = froot(glob(claim['local']), 73, 18816)
    checks = {
        'bit_c': (c, float(Fraction(bud['base']['bit_c']))),
        'complex_b': (b, float(Fraction(bud['base']['complex_b']))),
        'kappa': (fkappa(c, b), float(bud['base']['kappa_decimal'])),
        'cap': (fkappa(c, 1.0), float(bud['bit_cap']['kappa_decimal'])),
    }
    L = dict(claim['local']); L[1] -= 1
    checks['one_unit_b'] = (froot(glob(L), 73, 18816), float(bud['headroom']['delete_rank1_children_below'][0]['complex_b']))
    L = dict(claim['local']); L[1] -= 2
    b2 = froot(glob(L), 73, 18816)
    assert b2 > c and froot(glob({**claim['local'], 1: 2547}), 73, 18816) < c
    n = bud['kappa_above_one_percent']['complex_rank1_units_per_call_needed']
    s = float(Fraction(bud['kappa_above_one_percent']['min_common_saving_s_star']))
    assert froot(glob({**claim['local'], 1: 2548-n}), 73, 18816) >= s > froot(glob({**claim['local'], 1: 2548-n+1}), 73, 18816)
    assert abs(fkappa(s, s*1.0000001) - 0.01) < 1e-11
    for k, (x, y) in checks.items():
        assert abs(x-y) <= 1e-12*max(1, abs(y)) + 1e-15, (k, x, y)
        print(f'{k:12s} float {x:.18f} certified {y:.18f}')
    print('PASS_INDEPENDENT_FLOAT_CROSSCHECK')


if __name__ == '__main__':
    main()
