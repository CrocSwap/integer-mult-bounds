# SPDX-License-Identifier: Apache-2.0
"""Scope D: the complex endpoint and kappa of PR #3015 from its complete profile, with an own rational-interval
moment enclosure for every rank (cross-checked against the vendored check_accounting.moment of PR2804 on the ranks
that one tabulates), the exact gain over PR #2979, the improvement test, the pricing of profile deltas (census), and
the PR #3018 composition prediction.

M(a) = (1/(73 W)) sum_r n_r r (73/r)^a = sum_r n_r r exp(a (ln 73 - ln r)) / (73 W), increasing in a; the complex
endpoint C is the largest 24-digit decimal with M(C) < 1 (and M(C + 1e-24) > 1); kappa = C - 1e-46 - 1e-70.
ln r (r >= 1): r = 2^k x with 1 <= x < 2, ln x = 2 atanh((x-1)/(x+1)) by its series with the geometric tail, ln 2 =
2 atanh(1/3); exp(y) for 0 <= y < 1 by its Taylor series with the tail bound 2 y^N / N!; every bound is rounded
outward to the grid 10^-60.  Standard library only; Python 3.8-compatible syntax.
"""
from fractions import Fraction as Q

import audit_lib as AL
from audit_common import need

M = 73
W = 66304
CALLS = 666
E24 = Q(1, 10 ** 24)
KAPPA_TERMS = (Q(1, 10 ** 46), Q(1, 10 ** 70))
GRID = 10 ** 60
_LN = {}


def floor_g(x):
    return Q((x * GRID).__floor__(), GRID)


def ceil_g(x):
    return Q(-((-x * GRID).__floor__()), GRID)


def atanh_iv(z, N=80):
    """0 <= z < 1: (partial sum, partial sum + tail) of atanh(z) = sum z^(2j+1)/(2j+1)."""
    need(0 <= z < 1, 'kappa.ln: atanh argument')
    s, zp, z2 = Q(0), z, z * z
    for j in range(N):
        s += zp / (2 * j + 1)
        zp *= z2
    return s, s + zp / (2 * N + 1) / (1 - z2)


def ln_interval(r):
    """Enclosure of ln r for an integer r >= 1 (cached)."""
    if r in _LN:
        return _LN[r]
    need(isinstance(r, int) and r >= 1, 'kappa.ln: rank')
    k, x = 0, Q(r)
    while x >= 2:
        x /= 2
        k += 1
    l2 = atanh_iv(Q(1, 3))
    lx = atanh_iv((x - 1) / (x + 1))
    lo = floor_g(2 * (k * l2[0] + lx[0]))
    hi = ceil_g(2 * (k * l2[1] + lx[1]))
    _LN[r] = (lo, hi)
    return _LN[r]


def exp_interval(y_lo, y_hi, N=40):
    """Enclosure of exp over [y_lo, y_hi], 0 <= y_lo <= y_hi < 1."""
    need(0 <= y_lo <= y_hi < 1, 'kappa.exp: argument outside [0, 1)')
    out = []
    for y, up in ((y_lo, False), (y_hi, True)):
        t = s = Q(1)
        for j in range(1, N):
            t = t * y / j
            s += t
        if up:
            s += 2 * t * y / N            # tail bound sum_{j>=N} y^j/j! <= 2 y^N/N! for y <= (N+1)/2
            out.append(ceil_g(s))
        else:
            out.append(floor_g(s))
    return out[0], out[1]


def H(r, a):
    """Enclosure of r (73/r)^a."""
    l73, lr = ln_interval(M), ln_interval(r)
    L_lo, L_hi = l73[0] - lr[1], l73[1] - lr[0]
    need(L_lo > 0, 'kappa.rank: rank %d not below 73' % r)
    e_lo, e_hi = exp_interval(a * L_lo, a * L_hi)
    return r * e_lo, r * e_hi


def moment(profile, a, live=W):
    """Enclosure of M(a) for a complete profile {rank: count} (counts >= 0)."""
    lo = hi = Q(0)
    for r, n in profile.items():
        if n == 0:
            continue
        need(n > 0 and 0 < int(r) < M, 'kappa.profile: rank %r count %r' % (r, n))
        h_lo, h_hi = H(int(r), a)
        lo += n * h_lo
        hi += n * h_hi
    return floor_g(lo / (M * live)), ceil_g(hi / (M * live))


def accepts(enc):
    return enc[1] < 1


def rejects(enc):
    return enc[0] > 1


def endpoint_format(C):
    need((C * 10 ** 24).denominator == 1 and C > 0, 'kappa.endpoint_format: C is not a positive 24-digit decimal')


def endpoint_check(prof, C, mom=moment):
    """C accepted (upper end of the enclosure of M(C) below 1) and C + 1e-24 rejected (lower end above 1)."""
    lo, hi = mom(prof, C)
    need(accepts((lo, hi)), 'kappa.endpoint_accept: M(C) enclosure [%.3e, %.3e] - 1 not below 0'
         % (float(lo - 1), float(hi - 1)))
    lo2, hi2 = mom(prof, C + E24)
    need(rejects((lo2, hi2)), 'kappa.endpoint_reject: M(C + 1e-24) enclosure [%.3e, %.3e] - 1 not above 0'
         % (float(lo2 - 1), float(hi2 - 1)))
    return dict(C_moment_minus_1=['%.9e' % float(lo - 1), '%.9e' % float(hi - 1)],
                C_plus_1e24_moment_minus_1=['%.9e' % float(lo2 - 1), '%.9e' % float(hi2 - 1)],
                C_enclosure_width='%.2e' % float(hi - lo))


def two_impl(prof, a, vendored_moment):
    """kappa.two_impl: the own enclosure and the vendored one (PR2804's check_accounting.moment) at a intersect, and
    neither accepts what the other rejects."""
    own, ven = moment(prof, a), vendored_moment(prof, a)
    need(max(own[0], ven[0]) <= min(own[1], ven[1]), 'kappa.two_impl: enclosures %r and %r are disjoint' % (own, ven))
    need(accepts(own) == accepts(ven) and rejects(own) == rejects(ven), 'kappa.two_impl: verdicts differ at %s' % a)
    return dict(own=['%.3e' % float(own[0] - 1), '%.3e' % float(own[1] - 1)],
                vendored=['%.3e' % float(ven[0] - 1), '%.3e' % float(ven[1] - 1)], intersect=True)


def kappa_check(kappa, C):
    need(kappa == C - KAPPA_TERMS[0] - KAPPA_TERMS[1], 'kappa.kappa: CLAIM kappa != C - 1e-46 - 1e-70')


def gain_check(kappa_new, kappa_old, claimed_gain):
    gain = kappa_new - kappa_old
    need(gain > 0 and gain == claimed_gain, 'kappa.gain: kappa gain %s != claimed %s' % (gain, claimed_gain))
    return dict(gain=str(gain), gain_float='%.6e' % float(gain))


def improvement(prof_old, prof_new, C_new, C_old):
    need(rejects(moment(prof_old, C_new)) and accepts(moment(prof_new, C_old)),
         'kappa.improvement: the old profile is not rejected at the new C (or the new profile not accepted at the old C)')


def straddle(prof, C, mom=moment):
    """Bisection on [C, C + 1e-24] until the enclosure of M straddles 1: (lo_a accepted, hi_a rejected, S)."""
    lo_a, hi_a = C, C + E24
    for _ in range(1200):              # the vendored enclosure is ~1e-191 wide: about 560 halvings
        mid = (lo_a + hi_a) / 2
        e = mom(prof, mid)
        if accepts(e):
            lo_a = mid
        elif rejects(e):
            hi_a = mid
        else:
            return lo_a, hi_a, mid
    raise AL.AuditFail('kappa.root_bracket: no straddle point found')


def predict_endpoint(prof, C_start, span=Q(1, 10 ** 6)):
    """The 24-digit endpoint of a complete profile by bisection on the 24-digit grid from an accepted C_start:
    returns (C, kappa) with M(C) accepted and M(C + 1e-24) rejected."""
    lo = (C_start * 10 ** 24).__floor__()
    hi = ((C_start + span) * 10 ** 24).__floor__()
    need(accepts(moment(prof, Q(lo, 10 ** 24))) and rejects(moment(prof, Q(hi, 10 ** 24))),
         'kappa.predict: initial bracket')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        e = moment(prof, Q(mid, 10 ** 24))
        if accepts(e):
            lo = mid
        elif rejects(e):
            hi = mid
        else:
            raise AL.AuditFail('kappa.predict: the grid point %d straddles 1' % mid)
    C = Q(lo, 10 ** 24)
    return C, C - KAPPA_TERMS[0] - KAPPA_TERMS[1]


def price_delta(delta_per_call, a, calls=CALLS, live=W):
    """Enclosure of the change of M(a) when every call's local profile changes by delta_per_call {rank: change}."""
    lo = hi = Q(0)
    for r, d in delta_per_call.items():
        h_lo, h_hi = H(int(r), a)
        if d >= 0:
            lo += d * h_lo
            hi += d * h_hi
        else:
            lo += d * h_hi
            hi += d * h_lo
    return calls * lo / (M * live), calls * hi / (M * live)


def dec(q, digits):
    s = (q * 10 ** digits).__floor__()
    return '%d.%0*d' % (s // 10 ** digits, digits, s % 10 ** digits)
