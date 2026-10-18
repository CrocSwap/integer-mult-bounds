#!/usr/bin/env python3
"""Independent rational log/exp oracle for the mixed-overhead claims.

No primary/predecessor verifier is imported. Input hashes are independently fixed.
RESULT.json supplies claims to check, never mathematical acceptance decisions.
Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from math import factorial
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
GRID = Q(1, 10**24)
LOG_SCALE = 10**55
INPUTS = {
    'research/community-frontier1094-audit/ASSEMBLY.json':
        '1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045',
    'research/e8-bit-p111-tuned/tune/EXPECTED.json':
        'b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def integer(x, label):
    need(type(x) is int and x >= 0, label + ': nonnegative integer required')
    return x


@lru_cache(None)
def logarithm(x):
    """Enclose log(x) by a positive atanh series with an exact tail."""
    x = Q(x)
    need(x >= 1, 'logarithm domain')
    shifts = 0
    while x > 2:
        x /= 2
        shifts += 1

    def reduced(y):
        t = (y - 1) / (y + 1)
        low = sum((2*t**(2*j+1)/Q(2*j+1) for j in range(70)), Q(0))
        tail = 2*t**141 / (141*(1-t*t))
        return low, low + tail

    low, high = reduced(x)
    low2, high2 = reduced(Q(2))
    low += shifts*low2
    high += shifts*high2
    return (Q(low.numerator*LOG_SCALE // low.denominator, LOG_SCALE),
            Q(-(-high.numerator*LOG_SCALE // high.denominator), LOG_SCALE))


def exponential(x):
    """Taylor degree 23; successive omitted terms have ratio <=x/25."""
    need(0 <= x < 1, 'exponential domain')
    low = sum((x**j/factorial(j) for j in range(24)), Q(0))
    tail = x**24 / (factorial(24)*(1-x/25))
    return low, low+tail


@lru_cache(None)
def power(x, a):
    need(0 <= a <= Q(1, 100), 'oracle exponent domain')
    low, high = logarithm(x)
    return exponential(a*low)[0], exponential(a*high)[1]


def residual(hist, m, stock, a, bit=False):
    need(all(type(r) is int and 0 < r < m and type(n) is int and n >= 0
             for r, n in hist.items()), 'histogram domain')
    low = high = Q(-1)
    for r, n in hist.items():
        left, right = power(Q(m, r), a)
        coefficient = Q(r*n, m*stock)
        low += coefficient*left
        high += coefficient*right
    if bit:
        left, right = power(Q(m), a)
        coefficient = Q(32*m*sum(hist.values()), 10**16*stock)
        low += coefficient*left
        high += coefficient*right
    need(low <= high and high-low < Q(1, 10**50), 'oracle interval width')
    return low, high


def packed(mass, cap):
    """Concavity minimizer, derived solely from mass and the rank cap."""
    q, r = divmod(integer(mass, 'mass'), cap)
    answer = {cap: q} if q else {}
    if r:
        answer[r] = answer.get(r, 0)+1
    return answer


def histogram(raw):
    need(type(raw) is dict, 'claimed histogram object')
    result = {}
    for key, value in raw.items():
        rank = int(key)
        need(str(rank) == key and rank > 0, 'canonical rank key')
        result[rank] = integer(value, 'claimed multiplicity')
    return result


def change(hist, delta, times=1):
    result = dict(hist)
    for rank, n in delta.items():
        result[rank] = result.get(rank, 0)+times*n
    need(all(n >= 0 for n in result.values()), 'change exceeds available children')
    return {r: n for r, n in result.items() if n}


def interval_claim(raw, actual, passing, label):
    """Require the independent strict sign and compatible claimed enclosures."""
    need(type(raw) is list and len(raw) == 2, label + ': interval shape')
    claimed = tuple(Q(x) for x in raw)
    need(claimed[0] <= claimed[1], label + ': reversed interval')
    if passing:
        need(actual[1] < 0 and claimed[1] < 0, label + ': strict acceptance')
    else:
        need(actual[0] > 0 and claimed[0] > 0, label + ': strict rejection')
    need(max(claimed[0], actual[0]) <= min(claimed[1], actual[1]),
         label + ': disjoint primary and oracle intervals')


def bootstrap(b, c):
    """Iterate seven exact recurrence steps; do not use the primary closed form."""
    e = GRID
    s = min(c, (1-e)*b) - Q(1, 10**27)
    need(0 < s < c and s < (1-e)*b, 'bootstrap target')
    a = Q(384599, 10**10)
    for _ in range(7):
        previous = a
        a = (1-s)*s+s*previous
        need(previous < a < s and s < 1-a, 'bootstrap order')
    q = a*(1-2*e)
    g = (1-e)*q/(1+q)
    ticks = g*10**18
    k = Q((ticks.numerator-1)//ticks.denominator, 10**18)
    need(k < g <= k+Q(1, 10**18), 'strict grid floor')
    return k, g


def check_receipt(receipt, root=ROOT):
    """Check scientific claims; primary implementation-control counts are not replayed."""
    loaded = []
    for path, expected in INPUTS.items():
        raw = (Path(root)/path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == expected, 'oracle input pin: '+path)
        loaded.append(json.loads(raw))
    asm, bit = loaded
    need(receipt['status'] == 'PASS_CENTRE_SHARING_MIXED_OVERHEAD'
         and receipt['no_new_kappa'] is True, 'receipt scope')
    original = histogram(asm['complex_profile'])
    bit_hist = histogram(bit['nine']['profile'])
    m, stock, bit_m, bit_stock = 73, 14336, 64, bit['nine']['bit']['live']
    b, c = Q(asm['complex_lower']), Q(asm['bit_lower'])
    need(bit_stock == 28416, 'bit stock')
    need(original[8] == 1152, 'selected centre count')
    shared = change(original, {8: -576})
    cap = 1
    while 2*(cap+1)**2 < m*m:
        cap += 1
    need(cap == 51, 'derived halving cap')

    for name, hist, width, w, endpoint, surcharge in (
            ('complex', original, m, stock, b, False),
            ('bit', bit_hist, bit_m, bit_stock, c, True)):
        row = receipt['baseline'][name]
        interval_claim(row['pass_residual'], residual(hist, width, w, endpoint, surcharge),
                       True, name+' selected endpoint')
        interval_claim(row['fail_residual'], residual(hist, width, w, endpoint+GRID, surcharge),
                       False, name+' next selected endpoint')

    for name, endpoint in (('bit_endpoint', c), ('next_complex_endpoint', b+GRID)):
        row = receipt['mixed_overhead'][name]
        mass = integer(row['mass'], name+' mass')
        need(Q(row['endpoint']) == endpoint, name+': exponent')
        need(row['next_mass'] == mass+1, name+': adjacent mass')
        need(Q(row['mass_per_call']) == Q(mass, 144), name+': per-call mass')
        for offset, key, interval_key in ((0, 'partition', 'pass_residual'),
                                          (1, 'next_partition', 'fail_residual')):
            minimizer = packed(mass+offset, cap)
            need(histogram(row[key]) == minimizer, name+': concavity minimizer')
            actual = residual(change(shared, minimizer), m, stock, endpoint)
            interval_claim(row[interval_key], actual, offset == 0, name+' '+key)

    equal = receipt['equal_mass_control']
    added = histogram(equal['histogram'])
    need(all(r <= cap for r in added) and sum(r*n for r, n in added.items()) == 4608,
         'equal-mass domain')
    interval_claim(equal['residual'], residual(change(shared, added), m, stock, b+GRID),
                   True, 'equal-mass redistribution')

    assembly = receipt['assembly']
    selected = Q(asm['kappa'])
    need(bootstrap(b, c)[0] == selected, 'selected grid result')
    k_equal, g_equal = bootstrap(c, c)
    k_ample, g_ample = bootstrap(Q(3, 1000), c)
    need(Q(assembly['full_gain']) == k_equal == k_ample, 'equal-endpoint finite grid result')
    need(Q(assembly['equal_endpoint_grid_margin']) == g_equal-k_equal,
         'equal-endpoint grid margin')
    need(Q(assembly['ample_endpoint_grid_margin']) == g_ample-k_ample,
         'ample-endpoint grid margin')
    target = selected*Q(11, 10)
    need(Q(assembly['target']) == target, 'ten-percent target')
    cstar = Q(assembly['bit_endpoint'])
    need((cstar/GRID).denominator == 1 and c < cstar < Q(3, 1000), 'target endpoint grid')
    need(bootstrap(Q(3, 1000), cstar-GRID)[0] < target
         <= bootstrap(Q(3, 1000), cstar)[0], 'adjacent target endpoint')

    improved = receipt['quantized_improvement']
    b_improved = Q(improved['complex_endpoint'])
    need(b_improved == b+Q(1, 10**8), 'quantized-improvement endpoint')
    largest = receipt['mixed_overhead']['next_complex_endpoint']['mass']
    interval_claim(improved['residual'],
                   residual(change(shared, packed(largest, cap)), m, stock, b_improved),
                   True, 'quantized-improvement moment')
    need(Q(improved['conditional_recipe_kappa']) == bootstrap(b_improved, c)[0]
         > selected, 'quantized-improvement recipe result')

    for name, delta in (('bit_pure_removal', {1: -1}),
                         ('bit_zero_mass_reblocking', {1: -42, 42: 1})):
        row = receipt[name]
        count = integer(row['changes'], name+' changes')
        need(count > 0 and row['previous_changes'] == count-1, name+': adjacent counts')
        for number, field, passing in ((count, 'pass_residual', True),
                                        (count-1, 'fail_residual', False)):
            actual = residual(change(bit_hist, delta, number), bit_m, bit_stock, cstar, True)
            interval_claim(row[field], actual, passing, name+' '+field)

    # For all mixed pure removals, d_r/r decreases; rank one maximizes saving/mass.
    # Enclose R/d_1 independently, retaining the removed child's surcharge.
    before = residual(bit_hist, bit_m, bit_stock, cstar, True)
    left, right = power(Q(bit_m), cstar)
    coefficient = Q(1, bit_m*bit_stock)+Q(32*bit_m, 10**16*bit_stock)
    ratio = before[0]/(coefficient*right), before[1]/(coefficient*left)
    count = receipt['bit_pure_removal']['changes']
    need(count-1 < ratio[0] <= ratio[1] < count, 'mixed pure-removal mass obstruction')
    return {'mixed_mass_full': receipt['mixed_overhead']['bit_endpoint']['mass'],
            'mixed_mass_next': receipt['mixed_overhead']['next_complex_endpoint']['mass'],
            'pure_removal': count,
            'zero_mass_reblocking': receipt['bit_zero_mass_reblocking']['changes']}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--receipt', type=Path, default=PKG/'RESULT.json',
                        help='untrusted receipt to check; supports corruption controls')
    args = parser.parse_args()
    checked = check_receipt(json.loads(args.receipt.read_text()))
    print('PASS_CENTRE_SHARING_MIXED_ORACLE',
          ' '.join(str(k)+'='+str(v) for k, v in checked.items()), 'no_new_kappa')


if __name__ == '__main__':
    main()
