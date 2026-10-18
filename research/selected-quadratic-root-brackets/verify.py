#!/usr/bin/env python3
"""Two-sided rational screening of selected moment roots; not supplier adoption.

Aaron Wang / navinor, with help from chatgpt. Apache-2.0.
No primary pricing implementation is imported.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCALE = 1 << 160
ASSEMBLY = 'research/community-frontier1094-audit/ASSEMBLY.json'
OWNER = 'research/community-frontier1094-audit/INDEPENDENT1094.json'
BIT = 'research/e8-bit-p111-tuned/tune/EXPECTED.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def outward(lo, hi):
    require(lo <= hi, 'reversed interval')
    return (Q((lo*SCALE).__floor__(), SCALE), Q((hi*SCALE).__ceil__(), SCALE))


def atanh_log(x):
    z = (x-1)/(x+1)
    require(0 <= z <= Q(1, 3), 'log reduction outside [1,2]')
    power, total = z, Q(0)
    for j in range(72):
        total += 2*power/(2*j+1)
        power *= z*z
    tail = 2*power/(145*(1-z*z))
    return outward(total, total+tail)


@lru_cache(maxsize=None)
def logarithm(x):
    x = Q(x)
    require(x >= 1, 'log input below one')
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    lo, hi = atanh_log(x)
    two_lo, two_hi = atanh_log(Q(2))
    return outward(lo+k*two_lo, hi+k*two_hi)


def coefficients(profile, m, w, surcharge):
    require(isinstance(m, int) and isinstance(w, int) and m > 1 and w > 0,
            'invalid width or normalization')
    require(profile and all(isinstance(r, int) and isinstance(n, int)
                            and 0 < r < m and n > 0 for r, n in profile.items()),
            'invalid child profile')
    terms = [(Q(n*r, m*w), logarithm(Q(m, r))) for r, n in sorted(profile.items())]
    rho = Q(32*m*sum(profile.values()), 10**16*w) if surcharge else Q(0)
    if surcharge:
        terms.append((rho, logarithm(Q(m))))
    d = 1-sum(c for c, _ in terms)
    e_lo = sum(c*lo for c, (lo, hi) in terms)
    e_hi = sum(c*hi for c, (lo, hi) in terms)
    f_lo = sum(c*lo*lo for c, (lo, hi) in terms)
    f_hi = sum(c*hi*hi for c, (lo, hi) in terms)
    l_hi = max(hi for c, (lo, hi) in terms)
    require(d > 0 and e_lo > 0 and f_lo > 0, 'no positive saving domain')
    return d, e_lo, e_hi, f_lo, f_hi, l_hi, rho


def gain(a, e, f, ell=None):
    require(a >= 0 and e > 0 and f >= 0, 'invalid gain arguments')
    denominator = 1 if ell is None else 1-ell*a/3
    require(denominator > 0, 'majorant pole/domain')
    return e*a + f*a*a/(2*denominator)


def root_bracket(d, e, f, hi, ell=None):
    require(d > 0 and hi > 0 and gain(hi, e, f, ell) >= d,
            'unbracketed surrogate root')
    lo = Q(0)
    for _ in range(100):
        mid = (lo+hi)/2
        if gain(mid, e, f, ell) <= d:
            lo = mid
        else:
            hi = mid
    require(gain(lo, e, f, ell) <= d <= gain(hi, e, f, ell),
            'surrogate root sides')
    return lo, hi


def screen(profile, m, w, surcharge):
    d, e_lo, e_hi, f_lo, f_hi, l_hi, rho = coefficients(profile, m, w, surcharge)
    linear = d/e_lo
    require(l_hi*linear < 3, 'linear root ceiling crosses majorant pole')
    lower = root_bracket(d, e_hi, f_hi, linear, l_hi)[0]
    upper = root_bracket(d, e_lo, f_lo, linear)[1]
    require(0 < lower < upper < linear, 'screening bounds not nested')
    require(gain(lower, e_hi, f_hi, l_hi) < d, 'lower bound not strict')
    require(gain(upper, e_lo, f_lo) > d, 'upper bound not strict')
    return {'D': str(d), 'E': [str(e_lo), str(e_hi)],
            'F': [str(f_lo), str(f_hi)], 'L_upper': str(l_hi),
            'surcharge_coefficient': str(rho), 'linear_upper': str(linear),
            'root_lower': str(lower), 'root_upper': str(upper),
            'width': str(upper-lower),
            'log_bits': 160, 'log_terms': 72, 'bisection_steps': 100}


def reject(call, diagnostic):
    try:
        call()
    except ValueError as error:
        require(diagnostic in str(error), 'wrong rejection diagnostic')
    else:
        raise ValueError('negative control accepted')


def controls():
    require(logarithm(Q(1)) == (0, 0), 'log-one exact fixture')
    lo, hi = logarithm(Q(2))
    require(Q(693147180559945309, 10**18) < lo < hi
            < Q(693147180559945310, 10**18), 'log-two independent decimal fixture')
    # Algebraic fixture: a single exp(a) curve, D=1/2. The true root ln(2)
    # is bracketed by both rational surrogates with no selected-data dependency.
    low = root_bracket(Q(1,2), Q(1,2), Q(1,2), Q(1), Q(1))[0]
    high = root_bracket(Q(1,2), Q(1,2), Q(1,2), Q(1))[1]
    require(low < lo < hi < high, 'single-exponential fixture')
    # Independent exact root: M(a)=2^(a-1), a*=1. Use deliberately broad
    # rational log bounds rather than the logarithm implementation above.
    require(gain(Q(1), Q(1,3), Q(2,9)) == Q(4,9), 'dyadic lower fixture')
    require(gain(Q(1), Q(7,20), Q(49,200), Q(7,10)) == Q(469,920),
            'dyadic upper fixture')
    require(root_bracket(Q(1,2), Q(7,20), Q(49,200), Q(3,2), Q(7,10))[0] < 1
            < root_bracket(Q(1,2), Q(1,3), Q(2,9), Q(3,2))[1],
            'dyadic exact root outside surrogate bracket')
    reject(lambda: logarithm(Q(0)), 'log input below one')
    reject(lambda: gain(Q(3), Q(1), Q(1), Q(1)), 'majorant pole/domain')
    reject(lambda: screen({1: 1}, 2, 0, False), 'invalid width or normalization')
    reject(lambda: screen({2: 1}, 2, 2, False), 'invalid child profile')
    reject(lambda: screen({1: 4}, 2, 2, False), 'no positive saving domain')
    reject(lambda: root_bracket(Q(1), Q(1), Q(1), Q(1,10)), 'unbracketed surrogate root')
    plain = coefficients({1: 1}, 2, 2, False)
    charged = coefficients({1: 1}, 2, 2, True)
    rho = Q(32*2, 10**16*2)
    require(plain[0]-charged[0] == rho and charged[6] == rho
            and charged[1]-plain[1] == rho*lo
            and charged[2]-plain[2] == rho*hi
            and charged[3]-plain[3] == rho*lo*lo
            and charged[4]-plain[4] == rho*hi*hi,
            'surcharge exponential D/E/F contributions omitted')
    require(coefficients({2: 1}, 4, 2, True)[5]
            > coefficients({2: 1}, 4, 2, False)[5],
            'surcharge maximum logarithmic rate omitted')
    return 12


def evaluate():
    assembly = json.loads((ROOT / ASSEMBLY).read_text(encoding='utf-8'))
    owner = json.loads((ROOT / OWNER).read_text(encoding='utf-8'))
    bit = json.loads((ROOT / BIT).read_text(encoding='utf-8'))['nine']
    complex_profile = {int(r): n for r, n in assembly['complex_profile'].items()}
    require(complex_profile == {int(r): n for r,n in owner['owner']['profile'].items()},
            'independent owner/profile disagreement')
    require(sum(r*n for r,n in complex_profile.items()) == owner['owner']['rank_mass'],
            'independent rank mass disagreement')
    w = owner['price']['live']
    require(73*w-sum(r*n for r,n in complex_profile.items()) == owner['owner']['deficit'],
            'independent deficit disagreement')
    bit_profile = {int(r): n for r,n in bit['profile'].items()}
    require(sum(r*n for r,n in bit_profile.items()) == bit['bit']['rank_mass'],
            'bit rank mass disagreement')
    require(Q(bit['bit_lower']) == Q(assembly['bit_lower']), 'selected bit endpoint disagreement')
    require(assembly['surcharge_model'] == {'complex': False, 'bit': True}
            and all(row['surcharge'] for row in assembly['conservative_moments']),
            'selected surcharge contract disagreement')
    cases = [('native_complex', complex_profile, 73, w, False, assembly['complex_lower']),
             ('conservative_complex', complex_profile, 73, w, True, assembly['conservative_complex_lower']),
             ('bit', bit_profile, 64, bit['bit']['live'], True, assembly['bit_lower'])]
    results = []
    for name, profile, m, live, bad, endpoint in cases:
        result = screen(profile, m, live, bad)
        lower, upper, linear = map(Q, [result['root_lower'], result['root_upper'], result['linear_upper']])
        alpha = Q(endpoint)
        require(lower < alpha < alpha+Q(1,10**24) < upper,
                'published endpoint interval outside screening bracket')
        improvement = (linear-alpha)/(upper-lower)
        require(improvement > 100, 'quadratic screen did not materially narrow D/E')
        result.update(name=name, m=m, W=live, surcharge=bad, endpoint=endpoint,
                      rank_mass=sum(r*n for r,n in profile.items()),
                      narrowing_factor=str(improvement),
                      narrowing_factor_floor=improvement.__floor__())
        results.append(result)
    require(Q(results[1]['root_upper']) < Q(results[0]['linear_upper']),
            'conservative/native consistency')
    return {'sources': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
                        for p in (ASSEMBLY, OWNER, BIT)},
            'ledgers': results, 'controls': controls(),
            'scope': 'screening brackets only; no endpoint-grid certification, word replay or new kappa'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--result', type=Path, default=HERE / 'RESULT.json')
    args = parser.parse_args()
    result = evaluate()
    path = args.result
    if args.write:
        path.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    else:
        require(result == json.loads(path.read_text(encoding='utf-8')), 'result receipt mismatch')
    print('PASS_SELECTED_QUADRATIC_ROOT_BRACKETS ledgers=3 controls=12 '
          'narrowing_gt_100x surcharge_included no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError) as error:
        raise SystemExit('FAIL_SELECTED_QUADRATIC_ROOT_BRACKETS: '+str(error))
