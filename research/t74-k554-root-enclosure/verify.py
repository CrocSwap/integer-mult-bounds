#!/usr/bin/env python3
"""Independent exact enclosure of the pivot-566+554 T74 complex moment root.

For a profile H, dimension m and live stock W, the native complex moment is
    M(x) = sum_r H[r] (r/m)^(1-x) / W = sum_r (r H[r] / (m W)) * exp(x ln(m/r))
(research/native-complex-moment552/PROOF.md). The conservative model adds the
inherited fallback 32 m^2 N / 10^16 children of rank one, N = sum_r H[r]
(notes/three-stage-cover-assembly.tex), i.e. 32 m N exp(x ln m) / (10^16 W).
An endpoint e on a 10^-d grid is certified when M(e) < 1 < M(e + 10^-d).

Method, chosen to share no algorithm with the authors' engines (Mercator series
and binary range reduction with atanh((x-1)/(x+1))) or with earlier audits:
  ln 2, ln 3, ln 5 are fixed integer combinations of A = ln(16/15),
  B = ln(25/24), C = ln(81/80); ln 73 = ln 72 + ln(73/72); each ln(p/q) with
  p - q = 1 is 2 atanh(1/(p+q)). exp uses argument halving, a Taylor
  polynomial and repeated squaring. Every quantity is an integer multiple of
  2^-bits rounded outward, and the final comparisons are exact integer
  comparisons. Inconclusive signs fail closed.

Standard library only; imports and executes nothing from the repository or
from either source package. Aaron Wang, with help from opencode. Apache-2.0.
"""
import argparse
import hashlib
import json
import math
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.set_int_max_str_digits(0)   # the PR1928 endpoints have about 10,000 digits
INPUTS_SHA256 = '609c486efb1fe1e03ff2c84ba11085b231b9372e81fb2650bda821ce84e6e1ae'

# ln(p/q) = 2 atanh(1/(p+q)) for these unit-gap ratios; exponent vectors over (2, 3, 5).
RATIOS = {'A': ((16, 15), (4, -1, -1)), 'B': ((25, 24), (-3, -1, 2)), 'C': ((81, 80), (-4, 4, -1))}
# ln p = sum coefficient * ratio log, for p = 2, 3, 5.
PRIME_LOGS = {2: (7, 5, 3), 3: (11, 8, 5), 5: (16, 12, 7)}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def cdiv(a, b):
    return -((-a) // b)


def check_log_identities():
    """Exact check that PRIME_LOGS inverts the exponent vectors of RATIOS."""
    for i, (p, coeff) in enumerate(PRIME_LOGS.items()):
        vec = [sum(c * RATIOS[k][1][j] for c, k in zip(coeff, 'ABC')) for j in range(3)]
        require(vec == [int(i == j) for j in range(3)], 'log identity for %d' % p)
    for (num, den), vec in RATIOS.values():
        require(num - den == 1 and num * 2 ** max(0, -vec[0]) * 3 ** max(0, -vec[1]) * 5 ** max(0, -vec[2])
                == den * 2 ** max(0, vec[0]) * 3 ** max(0, vec[1]) * 5 ** max(0, vec[2]), 'ratio factorization')


def atanh_inv(k, bits):
    """Integer interval [lo, hi] containing 2^bits * atanh(1/k), k >= 2."""
    one, k2 = 1 << bits, k * k
    terms = int(bits / (2 * math.log2(k))) + 2
    plo, phi = one // k, cdiv(one, k)
    lo = hi = 0
    for j in range(terms):
        lo += plo // (2 * j + 1)
        hi += cdiv(phi, 2 * j + 1)
        plo, phi = plo // k2, cdiv(phi, k2)
    # remaining terms: sum_{j>=terms} k^-(2j+1)/(2j+1) <= k^-(2 terms+1) * k^2/((2 terms+1)(k^2-1)); phi bounds 2^bits k^-(2 terms+1)
    hi += cdiv(phi * k2, (2 * terms + 1) * (k2 - 1))
    return lo, hi


def combine(parts, coeffs):
    lo = sum(c * (p[0] if c > 0 else p[1]) for p, c in zip(parts, coeffs))
    hi = sum(c * (p[1] if c > 0 else p[0]) for p, c in zip(parts, coeffs))
    return lo, hi


def factor235(n):
    e = []
    for p in (2, 3, 5):
        k = 0
        while n % p == 0:
            n //= p
            k += 1
        e.append(k)
    require(n == 1, 'rank is not 5-smooth')
    return e


def log_table(m, ranks, bits):
    """Integer intervals for 2^bits ln(m/r); requires m = 73 (so m - 1 = 72 is 5-smooth)."""
    require(m == 73, 'this enclosure is written for m = 73')
    base = [tuple(2 * v for v in atanh_inv(num + den, bits)) for (num, den), _ in RATIOS.values()]
    d73 = tuple(2 * v for v in atanh_inv(73 + 72, bits))
    out = {}
    for r in ranks:
        require(0 < r < m, 'child rank range')
        e = [a - b for a, b in zip(factor235(72), factor235(r))]   # 72/r over (2, 3, 5)
        coeff = [sum(e[i] * PRIME_LOGS[p][j] for i, p in enumerate((2, 3, 5))) for j in range(3)]
        lo, hi = combine(base, coeff)
        out[r] = (lo + d73[0], hi + d73[1])
    return out


def exp_interval(ylo, yhi, bits):
    """Integer interval containing 2^bits exp(y) for 2^bits y in [ylo, yhi], 0 <= y < 1/2."""
    one = 1 << bits
    require(0 <= ylo <= yhi < one // 2, 'exp range')
    s = int(math.isqrt(bits)) + 1
    guard = s + 32
    w = bits + guard
    xlo, xhi = (ylo << guard) >> s, cdiv(yhi << guard, 1 << s)
    W1 = 1 << w
    slo = shi = tlo = thi = W1
    n = 0
    while True:
        n += 1
        tlo = ((tlo * xlo) >> w) // n
        thi = cdiv(cdiv(thi * xhi, W1), n)
        slo += tlo
        shi += thi
        if thi <= 1:
            break
    shi += thi + 1   # tail after term n is at most term n since x/(n+1) <= 1/2
    for _ in range(s):
        slo = (slo * slo) >> w
        shi = cdiv(shi * shi, W1)
    return slo >> guard, cdiv(shi, 1 << guard)


def scaled_product(x, lohi):
    """Interval of 2^bits * x * L for exact x > 0 and L given by an integer interval."""
    return (x.numerator * lohi[0]) // x.denominator, cdiv(x.numerator * lohi[1], x.denominator)


def side(src, x, surcharge, bits, m=None, profile=None, live=None):
    """-1 if M(x) < 1, +1 if M(x) > 1, 0 if the enclosure at this precision cannot decide."""
    m = m or 73
    profile = profile or {int(r): int(n) for r, n in src['global_profile'].items()}
    live = live or int(src['live'])
    logs = log_table(m, tuple(sorted(set(profile) | {1})), bits)
    lo_sum = hi_sum = 0
    for r, n in profile.items():
        if r == m:
            elo = ehi = 1 << bits
        else:
            elo, ehi = exp_interval(*scaled_product(x, logs[r]), bits)
        lo_sum += r * n * elo
        hi_sum += r * n * ehi
    target = m * live << bits
    if surcharge:
        N = sum(profile.values())
        elo, ehi = exp_interval(*scaled_product(x, logs[1]), bits)
        lo_sum, hi_sum, target = (10 ** 16 * lo_sum + 32 * m * m * N * elo,
                                  10 ** 16 * hi_sum + 32 * m * m * N * ehi, 10 ** 16 * target)
    if hi_sum < target:
        return -1
    if lo_sum > target:
        return 1
    return 0


def default_bits(digits):
    return int(digits * math.log2(10)) + 128


def bracket(src, surcharge, endpoint=None, bits=None, **model):
    d = int(src['grid_digits'])
    grid = Q(1, 10 ** d)
    e = Q(endpoint if endpoint is not None else src['conservative_complex_lower' if surcharge else 'complex_lower'])
    bits = bits or default_bits(d)
    at, nxt = side(src, e, surcharge, bits, **model), side(src, e + grid, surcharge, bits, **model)
    for _ in range(2):   # refine only an undecided sign; never accept an undecided one
        if at and nxt:
            break
        bits *= 2
        at, nxt = side(src, e, surcharge, bits, **model), side(src, e + grid, surcharge, bits, **model)
    on_grid = (e * 10 ** d).denominator == 1
    return {'on_grid': on_grid, 'endpoint_side': at, 'next_side': nxt, 'bits': bits,
            'pass': on_grid and at == -1 and nxt == 1}


def ledger(src):
    m, live = 73, int(src['live'])
    total = {}
    for p, cnt in src['provider_counts'].items():
        for r, n in src['provider_profiles'][p].items():
            total[int(r)] = total.get(int(r), 0) + int(cnt) * int(n)
    for r, n in src['idle_remainder_profile'].items():
        total[int(r)] = total.get(int(r), 0) + int(n)
    glob = {int(r): int(n) for r, n in src['global_profile'].items()}
    require(total == glob, 'provider profiles and idle remainder do not sum to the global profile')
    mass = sum(r * n for r, n in glob.items())
    require(mass == int(src['rank_mass']), 'rank mass')
    require(max(glob) < m, 'child rank range')
    return dict(calls=sum(int(c) for c in src['provider_counts'].values()), children=sum(glob.values()),
                rank_mass=mass, deficit=m * live - mass)


def controls(src, names=None):
    """Each semantic mutation must make the bracket fail; True means rejected."""
    d = int(src['grid_digits'])
    g = Q(1, 10 ** d)
    nat, con = Q(src['complex_lower']), Q(src['conservative_complex_lower'])
    prof = {int(r): int(n) for r, n in src['global_profile'].items()}
    moved = {**prof, 1: prof[1] - 1, 2: prof[2] + 1}
    cases = {
        'next_grid_as_endpoint': lambda: bracket(src, False, endpoint=nat + g),
        'previous_grid_as_endpoint': lambda: bracket(src, False, endpoint=nat - g),
        'one_child_rank1_to_rank2': lambda: bracket(src, False, profile=moved),
        'dimension_72': lambda: _m72(src),
        'live_minus_one': lambda: bracket(src, False, live=int(src['live']) - 1),
        'conservative_endpoint_without_surcharge': lambda: bracket(src, False, endpoint=con),
        'native_endpoint_with_surcharge': lambda: bracket(src, True, endpoint=nat),
    }
    out = {}
    for name, run in cases.items():
        if names is None or name in names:
            out[name] = not run()['pass']
    return out


def _m72(src):
    """m = 72 cannot use the m = 73 log table; evaluate it with ln(72/r) = ln(73/r) - ln(73/72)."""
    d = int(src['grid_digits'])
    bits = default_bits(d)
    e, g = Q(src['complex_lower']), Q(1, 10 ** d)
    prof = {int(r): int(n) for r, n in src['global_profile'].items()}
    logs = log_table(73, tuple(sorted(set(prof) | {1})), bits)
    d73 = tuple(2 * v for v in atanh_inv(145, bits))

    def sgn(x):
        lo_sum = hi_sum = 0
        for r, n in prof.items():
            l = (logs[r][0] - d73[1], logs[r][1] - d73[0])
            elo, ehi = exp_interval(*scaled_product(x, l), bits)
            lo_sum += r * n * elo
            hi_sum += r * n * ehi
        t = 72 * int(src['live']) << bits
        return -1 if hi_sum < t else (1 if lo_sum > t else 0)
    return {'pass': sgn(e) == -1 and sgn(e + g) == 1}


def load_inputs():
    return json.loads((HERE / 'INPUTS.json').read_text(encoding='utf-8'))


def check_inputs_pin():
    require(hashlib.sha256((HERE / 'INPUTS.json').read_bytes()).hexdigest() == INPUTS_SHA256, 'INPUTS.json pin')


def run():
    check_inputs_pin()
    check_log_identities()
    inputs = load_inputs()
    coarse, fine = inputs['sources']['pr1672'], inputs['sources']['pr1928']
    result = dict(status=None, inputs_sha256=INPUTS_SHA256, m=inputs['m'], ledgers={}, brackets={}, nesting={}, controls={})
    for key, src in inputs['sources'].items():
        result['ledgers'][key] = ledger(src)
        for model, surcharge in (('native', False), ('conservative', True)):
            b = bracket(src, surcharge)
            result['brackets']['%s/%s' % (key, model)] = b
    for model, field in (('native', 'complex_lower'), ('conservative', 'conservative_complex_lower')):
        e70, e10k = Q(coarse[field]), Q(fine[field])
        floor70 = Q((e10k * 10 ** 70).__floor__(), 10 ** 70)
        result['nesting'][model] = dict(coarse_equals_floor_of_fine=(floor70 == e70))
    result['controls']['pr1672'] = controls(coarse)
    result['controls']['pr1928'] = controls(fine, ('next_grid_as_endpoint', 'previous_grid_as_endpoint',
                                                   'conservative_endpoint_without_surcharge'))
    result['headline_kappa_below_native_endpoint'] = {
        key: dict(below=Q(src['headline_kappa']) < Q(src['complex_lower']),
                  endpoint_minus_kappa=_sci(Q(src['complex_lower']) - Q(src['headline_kappa'])))
        for key, src in inputs['sources'].items()}
    result['scope'] = ('Native and conservative complex moment brackets and the profile composition only. The outer '
                       'reduction that turns the endpoint into each headline kappa is not checked here.')
    ok = (all(b['pass'] for b in result['brackets'].values()) and all(n['coarse_equals_floor_of_fine'] for n in result['nesting'].values())
          and all(all(c.values()) for c in result['controls'].values())
          and all(h['below'] for h in result['headline_kappa_below_native_endpoint'].values()))
    require(ok, 'enclosure failed: ' + json.dumps(result, default=str)[:2000])
    result['status'] = 'PASS_T74_K554_ROOT_ENCLOSURE_INDEPENDENT'
    return result


def _sci(x):
    sign = '-' if x < 0 else ''
    x = abs(x)
    if x == 0:
        return '0'
    e = math.floor(math.log10(x.numerator) - math.log10(x.denominator))
    mant = x / Q(10) ** e
    while mant >= 10:
        mant, e = mant / 10, e + 1
    while mant < 1:
        mant, e = mant * 10, e - 1
    return '%s%se%d' % (sign, str(Q((mant * 10 ** 9).__floor__(), 10 ** 9).__float__()), e)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--write', action='store_true', help='rewrite RESULT.json instead of comparing with it')
    a = ap.parse_args()
    t0 = time.perf_counter()
    result = run()
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    path = HERE / 'RESULT.json'
    if a.write:
        path.write_text(text, encoding='utf-8', newline='\n')
    else:
        require(path.read_text(encoding='utf-8') == text, 'RESULT.json differs from this run')
    n_ctl = sum(len(c) for c in result['controls'].values())
    print('%s | brackets %d | nesting %d | controls %d rejected | %.1f s' % (
        result['status'], len(result['brackets']), len(result['nesting']), n_ctl, time.perf_counter() - t0))


if __name__ == '__main__':
    main()
