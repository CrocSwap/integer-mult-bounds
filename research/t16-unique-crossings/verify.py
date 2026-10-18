"""Unique T16 moment crossings with exact log/Taylor enclosures. Apache-2.0."""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def log_series(x):
    z = (x - 1) / (x + 1)
    need(0 <= z <= Q(1, 3), 'log reduction')
    n = 60
    low = 2 * sum((z ** (2 * j + 1) / (2 * j + 1) for j in range(n)), Q(0))
    tail = 2 * z ** (2 * n + 1) / ((2 * n + 1) * (1 - z * z))
    return low, low + tail


@lru_cache(None)
def log_rank(r):
    k = r.bit_length() - 1
    a, b = log_series(Q(r, 1 << k))
    c, d = log_series(Q(2))
    lo, hi = a + k * c, b + k * d
    scale = 1 << 80
    return Q((lo * scale).__floor__(), scale), Q((hi * scale).__ceil__(), scale)


def exp_interval(x):
    need(0 <= x <= 4, 'exponential domain')
    term = total = Q(1)
    n = 52
    for j in range(1, n + 1):
        term = term * x / j
        total += term
    first = term * x / (n + 1)
    return total, total + first / (1 - x / (n + 2))


def evaluate(delta, a):
    need(0 <= a <= 1, 'moment domain')
    low = high = Q(0)
    for r, c in delta.items():
        ll, lu = log_rank(r)
        lo = exp_interval((1 - a) * ll)[0]
        hi = exp_interval((1 - a) * lu)[1]
        low += c * (lo if c > 0 else hi)
        high += c * (hi if c > 0 else lo)
    return low, high


def sign(delta, a):
    lo, hi = evaluate(delta, a)
    need(lo > 0 or hi < 0, 'unresolved strict sign')
    return 1 if lo > 0 else -1


def certify_shape(delta):
    items = sorted(delta.items())
    need(len(items) == 4 and items[0][0] == 1, 'four distinct ranks starting at one')
    need([c > 0 for _, c in items] == [True, False, False, True], 'required coefficient signs')
    need(sum(r * c for r, c in items) == 0, 'equal mass gives p=1 root')
    need(sum(c for _, c in items) > 0, 'positive p=0 endpoint')
    numerator = denominator = 1
    for r, c in items:
        if c > 0:
            numerator *= r ** (r * c)
        else:
            denominator *= r ** (-r * c)
    need(numerator > denominator, 'positive derivative at p=1')
    return {'log_derivative_numerator': numerator, 'log_derivative_denominator': denominator,
            'p_one_root': True, 'p_zero_value': sum(delta.values()),
            'maximum_real_roots': 2, 'interior_roots': 1}


def run():
    for row in json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'source pin ' + row['path'])
    previous = json.loads((ROOT / 'research/t16-moment-order-audit/EVIDENCE.json').read_text())
    pairs = [x for x in previous['pairs'] if x['final_order'] == 'certified_crossing']
    need(len(pairs) == 3, 'exact predecessor crossing domain')
    results = []
    for pair in pairs:
        delta = {int(r): c for r, c in pair['delta'].items()}
        proof = certify_shape(delta)
        lo, hi = 1, 1024
        need(sign(delta, Q(lo, 1024)) == -1 and sign(delta, Q(hi, 1024)) == 1, 'strict bracket')
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if sign(delta, Q(mid, 1024)) < 0:
                lo = mid
            else:
                hi = mid
        lower, upper = Q(lo, 1024), Q(hi, 1024)
        left, right = evaluate(delta, lower), evaluate(delta, upper)
        # Independent coarse sign validation: rational powers at a=1/2 via
        # exact squared-integer brackets, not log or Taylor arithmetic.
        scale = 1 << 40
        import math
        lows = highs = Q(0)
        for r, c in delta.items():
            root = math.isqrt(r * scale * scale)
            l, u = Q(root, scale), Q(root + (root * root != r * scale * scale), scale)
            lows += c * (l if c > 0 else u)
            highs += c * (u if c > 0 else l)
        need((highs < 0 and sign(delta, Q(1, 2)) < 0) or
             (lows > 0 and sign(delta, Q(1, 2)) > 0), 'independent sqrt sign')
        # Avoid huge presentation fractions while retaining exact enclosure.
        rounding = 1 << 64
        enclosure = lambda interval: [str(Q((interval[0] * rounding).__floor__(), rounding)),
                                      str(Q((interval[1] * rounding).__ceil__(), rounding))]
        results.append({'old': pair['old'], 'new': pair['new'], 'delta': pair['delta'],
                        'proof': proof, 'a_interval': [str(lower), str(upper)],
                        'lower_delta': enclosure(left), 'upper_delta': enclosure(right)})
    controls = []
    for name, bad in [('unequal_mass', {1: 8, 3: -3, 7: -2, 16: 1}),
                      ('wrong_sign_shape', {1: -7, 3: 3, 7: 2, 16: -1}),
                      ('missing_term', {1: 7, 3: -3, 16: 1}),
                      ('wrong_derivative', {1: 3, 2: -2, 3: -1, 4: 1})]:
        try:
            certify_shape(bad)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('invalid theorem premise accepted ' + name)
    common = min(Q(row['a_interval'][0]) for row in results)
    return {'status': 'PASS_T16_UNIQUE_CROSSINGS', 'crossings': results,
            'common_strict_favorable_interval': ['0', str(common)],
            'rejected_controls': controls, 'new_kappa': False}


if __name__ == '__main__':
    result = run()
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    else:
        need(result == json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8')), 'receipt')
    print(result['status'], 'crossings=3 common_a<' + result['common_strict_favorable_interval'][1])
