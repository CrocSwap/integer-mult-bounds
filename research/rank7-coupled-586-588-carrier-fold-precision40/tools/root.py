#!/usr/bin/env python3
"""root.py -- exact (rational-bracketed) complex endpoint kappa from a complete global profile.

The T-replica network has 9*T calls, live width W = 896*T, base m = 73.  A complete paid profile
{rank: count} (local jumps of all calls + idle/remainder children of all bins) has the moment

    M(b) = sum_r count_r * r * (73/r)^b / (73 * W)          (= audit_owners.moment(profile, b, W))

which is increasing in b; the complex endpoint is the root M(b) = 1.  PR2857's headline is
floor(root_lower, 24 digits) - 1e-46 - 1e-70; PR2853/PR2833's headlines are their roots - O(1e-3022).
The rational interval arithmetic (log via atanh series, exp via Taylor, outward rounding at 10^-45)
is the package's own, so the brackets coincide exactly with the independent audits.

Rank-mass identity for a complete profile: sum_r r*count_r = 65088*T  (= (73-1)*896*T + 64*9*T).

Usage:
  python -B root.py --calibrate                      # PR2857 / PR2853 / PR2833 reproduction
  python -B root.py --profile '{"1":805860,...}' --T 37 [--delta '{"1":9,"2":-9}'] [--digits 25]
  python -B root.py --profile-file PROFILE.json --T 37 --table      # per-rank derivative table
API:
  kappa_from_profile(profile, T, digits=25) -> (lo, hi)  exact Fractions, M(lo)<1<M(hi) certified
  delta_value(profile, T, delta)            -> dict with new bracket and exact gain interval
  derivatives(profile, T)                   -> {rank: dkappa/dcount_r} (mpmath, 40 digits)
"""
from fractions import Fraction as Q
from functools import lru_cache
import argparse, json, sys

M_BASE = 73
LIVE_PER_REPLICA = 896
CALLS_PER_REPLICA = 9
MASS_PER_REPLICA = (M_BASE - 1) * LIVE_PER_REPLICA + 64 * CALLS_PER_REPLICA  # 65088
SCALE = 10 ** 45


def need(c, m):
    if not c:
        raise ValueError(m)


@lru_cache(None)
def logarithm(x):
    """Rational enclosure of log(x), x >= 1 (package arithmetic, outward rounding 10^-45)."""
    need(x >= 1, 'log argument')
    k = 0
    while x >= 2:
        x /= 2
        k += 1

    def unit(y):
        z = (y - 1) / (y + 1)
        power = z
        total = Q(0)
        for j in range(100):
            total += power / (2 * j + 1)
            power *= z * z
        total *= 2
        tail = 2 * power / (201 * (1 - z * z))
        return total, total + tail

    lo, hi = unit(x)
    l2, h2 = unit(Q(2))
    lo += k * l2
    hi += k * h2
    return Q((lo * SCALE).__floor__(), SCALE), Q((hi * SCALE).__ceil__(), SCALE)


def exponential(x):
    need(0 <= x < 1, 'exp argument')
    term = total = Q(1)
    for j in range(1, 19):
        term *= x / j
        total += term
    tail = term * x / 19 / (1 - x / 20)
    return total, total + tail


def H(rank, b):
    """Enclosure of H_r(b) = r*(73/r)^b  (the moment of one rank-r child times 73)."""
    l, h = logarithm(Q(M_BASE, rank))
    return rank * exponential(b * l)[0], rank * exponential(b * h)[1]


def moment(profile, b, W):
    """Enclosure of sum_r count_r * r * (73/r)^b / (73*W); counts may be Fractions (>=0)."""
    lo = hi = Q(0)
    for rank, count in profile.items():
        if count == 0:
            continue
        need(0 < rank < M_BASE and count > 0, 'child profile')
        e0, e1 = H(rank, b)
        lo += Q(count) * e0 / (M_BASE * W)
        hi += Q(count) * e1 / (M_BASE * W)
    return Q((lo * SCALE).__floor__(), SCALE), Q((hi * SCALE).__ceil__(), SCALE)


def normalize(profile):
    out = {}
    for r, n in profile.items():
        r = int(r)
        n = Q(n) if not isinstance(n, int) else n
        if n:
            out[r] = out.get(r, 0) + n
    return out


def rank_mass(profile):
    return sum(r * Q(n) for r, n in normalize(profile).items())


def root_bracket(profile, W, digits=25, check_mass_T=None):
    """Bisection on the grid 10^-digits: returns (lo, hi) with M(lo) < 1 < M(hi) certified."""
    profile = normalize(profile)
    if check_mass_T is not None:
        need(rank_mass(profile) == MASS_PER_REPLICA * check_mass_T, 'rank-mass identity (incomplete profile?)')
    G = 10 ** digits
    low, high = 0, G // 100
    need(moment(profile, Q(low, G), W)[1] < 1 < moment(profile, Q(high, G), W)[0], 'root initial interval')
    while high - low > 1:
        mid = (low + high) // 2
        a, b = moment(profile, Q(mid, G), W)
        if b < 1:
            low = mid
        elif a > 1:
            high = mid
        else:
            raise ValueError('root interval precision exhausted at %d digits' % digits)
    return Q(low, G), Q(high, G)


def kappa_from_profile(profile, T, digits=25, strict_mass=True):
    """Exact bracket of the complex endpoint for a complete global profile of a T-replica network."""
    return root_bracket(profile, LIVE_PER_REPLICA * T, digits, T if strict_mass else None)


def add_profiles(a, b, scale_b=1):
    out = dict(normalize(a))
    for r, n in normalize(b).items():
        out[r] = out.get(r, 0) + scale_b * n
        need(out[r] >= 0, 'negative count at rank %d' % r)
        if out[r] == 0:
            del out[r]
    return out


def delta_value(profile, T, delta, digits=25, strict_mass=True):
    """Value (exact root brackets) of changing the complete profile by delta = {rank: +-count}."""
    base = kappa_from_profile(profile, T, digits, strict_mass)
    newp = add_profiles(profile, delta)
    mass_ok = rank_mass(newp) == MASS_PER_REPLICA * T
    new = kappa_from_profile(newp, T, digits, strict_mass and mass_ok)
    return dict(base_lower=str(base[0]), base_upper=str(base[1]), new_lower=str(new[0]), new_upper=str(new[1]),
                gain_lower=str(new[0] - base[1]), gain_upper=str(new[1] - base[0]),
                gain_float=float((new[0] + new[1] - base[0] - base[1]) / 2), new_profile={str(r): str(n) for r, n in sorted(newp.items())},
                new_rank_mass_identity=mass_ok, note=None if mass_ok else 'delta breaks the rank-mass identity: a derivative probe, not a complete legal profile (a legal word change moves local mass and inventory/idle mass together)')


def derivatives(profile, T, b=None):
    """dkappa/dcount_r (per single child of rank r) by the implicit function theorem, mpmath 40 digits."""
    import mpmath
    mpmath.mp.dps = 40
    profile = normalize(profile)
    W = LIVE_PER_REPLICA * T
    if b is None:
        lo, hi = kappa_from_profile(profile, T, strict_mass=False)
        b = (lo + hi) / 2
    b = mpmath.mpf(b.numerator) / b.denominator
    dMdb = mpmath.mpf(0)
    for r, n in profile.items():
        dMdb += mpmath.mpf(n) * r * mpmath.power(mpmath.mpf(M_BASE) / r, b) * mpmath.log(mpmath.mpf(M_BASE) / r) / (M_BASE * W)
    out = {}
    for r in range(1, M_BASE):
        dMdn = r * mpmath.power(mpmath.mpf(M_BASE) / r, b) / (M_BASE * W)
        out[r] = -dMdn / dMdb
    return out, b


def fmt(x, nd=28):
    return mpmath_str(x, nd)


def mpmath_str(x, nd):
    import mpmath
    mpmath.mp.dps = nd + 5
    return mpmath.nstr(mpmath.mpf(x.numerator) / x.denominator if isinstance(x, Q) else x, nd)


CALIBRATION = {
    'PR2857': dict(T=37, profile={1: 805860, 2: 213786, 3: 91775, 4: 42624, 5: 13098, 8: 2664, 9: 1, 48: 13379},
                   expected_lower='17200966286848326009728/10000000000000000000000000',
                   expected_upper='17200966286848326009729/10000000000000000000000000',
                   headline='0.001720096628684832600972 - 1e-46 - 1e-70 (CLAIM.json)'),
    'PR2853': dict(T=74, profile={1: 1616713, 2: 424908, 3: 183207, 4: 85249, 5: 26625, 6: 58, 7: 3, 8: 5328, 32: 47, 48: 26703},
                   headline='0.00171937765869758665904733841726077218140089564514 (outer/OUTER-CLAIM.json, = C - 1e-3046 - 1e-3022)'),
    'PR2833': dict(T=74, profile={1: 1603728, 2: 432900, 3: 183683, 4: 85248, 5: 26862, 8: 5328, 9: 1, 48: 26625},
                   headline='0.00171865743716685595569345761432428040996497469293 (outer/OUTER-CLAIM.json)'),
}


def calibrate(digits=25):
    results = {}
    for name, c in CALIBRATION.items():
        lo, hi = kappa_from_profile(c['profile'], c['T'], digits)
        row = dict(T=c['T'], profile=c['profile'], lower=str(lo), upper=str(hi), lower_decimal=mpmath_str(lo, digits),
                   upper_decimal=mpmath_str(hi, digits), headline=c['headline'], rank_mass=str(rank_mass(c['profile'])))
        if 'expected_lower' in c:
            row['reproduces_package_bracket'] = (lo == Q(c['expected_lower']) and hi == Q(c['expected_upper']))
        else:
            head = c['headline'].split(' ')[0]
            row['headline_inside_bracket'] = (Q(head) >= lo - Q(1, 10 ** 22)) and (Q(head) <= hi)
            dec = mpmath_str(lo, digits)
            k = 0
            while k < min(len(dec), len(head)) and dec[k] == head[k]:
                k += 1
            row['matches_headline_to_digits'] = k - 2  # decimals in common ('0.' excluded)
        results[name] = row
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--calibrate', action='store_true')
    ap.add_argument('--profile', help='JSON {rank: count}')
    ap.add_argument('--profile-file')
    ap.add_argument('--T', type=int, default=37)
    ap.add_argument('--delta', help='JSON {rank: +-count} (complete-profile change, e.g. 9*T per-call units)')
    ap.add_argument('--per-call-delta', help='JSON {rank: +-count per call}; multiplied by 9*T')
    ap.add_argument('--digits', type=int, default=25)
    ap.add_argument('--table', action='store_true', help='print per-rank derivative table')
    ap.add_argument('--no-mass-check', action='store_true')
    a = ap.parse_args()
    if a.calibrate:
        print(json.dumps(calibrate(a.digits), indent=1, sort_keys=True))
        return
    profile = json.loads(a.profile) if a.profile else json.load(open(a.profile_file))
    profile = {int(k): (int(v) if str(v).lstrip('-').isdigit() else Q(v)) for k, v in profile.items()}
    strict = not a.no_mass_check
    lo, hi = kappa_from_profile(profile, a.T, a.digits, strict)
    out = dict(T=a.T, W=LIVE_PER_REPLICA * a.T, lower=str(lo), upper=str(hi), lower_decimal=mpmath_str(lo, a.digits),
               rank_mass=str(rank_mass(profile)))
    if a.delta or a.per_call_delta:
        d = {int(k): int(v) for k, v in json.loads(a.delta or a.per_call_delta).items()}
        if a.per_call_delta:
            d = {k: v * CALLS_PER_REPLICA * a.T for k, v in d.items()}
        out['delta'] = delta_value(profile, a.T, d, a.digits, strict)
    if a.table:
        der, b = derivatives(profile, a.T)
        out['derivative_per_child'] = {str(r): mpmath_str(v, 12) for r, v in der.items() if r in profile or r <= 9 or r == 48}
        out['derivative_per_call_unit'] = {str(r): mpmath_str(v * CALLS_PER_REPLICA * a.T, 12) for r, v in der.items() if r in profile or r <= 9 or r == 48}
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
