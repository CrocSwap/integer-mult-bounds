# SPDX-License-Identifier: Apache-2.0
"""Directed rational price, tail, input-lift and fixed-profile bounds."""

from fractions import Fraction as Q
from functools import lru_cache

from word import require

GRID = 2**160


def enclose(lo, hi):
    return Q(lo * GRID // 1, GRID), Q(-(-hi * GRID // 1), GRID)


def log_near_one(x):
    t = (x - 1) / (x + 1)
    term, lo = t, Q(0)
    for j in range(64):
        lo += 2 * term / (2 * j + 1)
        term *= t * t
    return lo, lo + 2 * term / (129 * (1 - t * t))


@lru_cache(None)
def log(r):
    k = r.bit_length() - 1
    lo, hi = log_near_one(Q(r, 2**k))
    a, b = log_near_one(Q(2))
    return enclose(lo + k*a, hi + k*b)


def exp_minus(x):
    # Odd truncation is a lower bound and the next even one is an upper bound.
    s, t = Q(1), Q(1)
    for j in range(1, 46):
        t *= -x / j
        s += t
    return s, s - t*x/46


@lru_cache(None)
def power(r, saving):
    lo, hi = log(r)
    lo, hi = enclose(abs(saving)*lo, abs(saving)*hi)
    require(0 <= lo <= hi < 1, "Alternating exponential domain")
    a, b = enclose(exp_minus(hi)[0], exp_minus(lo)[1])
    return enclose(r/b, r/a) if saving < 0 else (r*a, r*b)


def moment(hist, saving):
    lo = hi = Q(0)
    for r, count in hist.items():
        a, b = power(r, saving)
        lo += count * (a if count >= 0 else b)
        hi += count * (b if count >= 0 else a)
    return lo, hi


def derivative_upper(hist, cap):
    result = Q(0)
    for r, count in hist.items():
        lo, hi = log(r)
        if count < 0:
            result -= count * r * hi
        else:
            result -= count * power(r, cap)[0] * lo
    return result


def certified_price(paid, target, prior, native_paid, physical_cap, gate):
    k, C = Q(gate["claim"]), Q(gate["tested"])
    lo, hi = map(Q, gate["raw_bracket"])
    bit = Q(gate["BIT_pin"])
    signed = {r: target.get(r, 0) - paid.get(r, 0) for r in target.keys() | paid.keys()}
    left, right = moment(signed, lo)[0], moment(signed, hi)[1]
    tested = moment(signed, C)[0]
    previous = moment(prior, k)[1]
    require(0 < k < C < lo < hi < bit and tested > 0 and left > 0 > right,
            "Directed raw crossing and tested price")
    require(previous < 0 and derivative_upper(signed, bit) < 0, "Source rejects new price; directed derivative")

    lower_target = moment(target, C)[0]
    alpha = moment(paid, C)[1] / lower_target
    gamma = moment(paid, C-Q(1, 7))[1] / (11 / power(11, Q(1, 7))[1] * lower_target)
    delta = sum(target.values()) * 12 / (11 / power(11, C)[1] * lower_target)
    reserve, decay, v = Q(1, 10**27), Q(31, 32), 1920
    require(alpha < 1-reserve and gamma < decay and delta < decay, "Tail and completion margins")
    require(1/(1+v*reserve) + 4*decay**v < 1, "Separated paid ceiling and target floor")
    require(11**64 < 12**63 and 2*(11**v)**64 <= (153**v)**63, "Completion geometry")

    a, b = [x/153 for x in power(153, C)]
    eta = (1-C)*a**v, (1-C)*b**v
    log_power = gate["written_log_power"]
    require(eta[1] <= Q(63, 64)**(log_power-2) and eta[0] > Q(63, 64)**(log_power-1)
            and a**(-v) < 2**log_power, "Minimum and written logarithmic powers")
    H, g = int(gate["H"]), (C-k)/7
    require(g.numerator == 1 and H % g.denominator == 0, "Integer funding comparison")
    h = H // g.denominator
    require((H+1)**log_power < 2**h and (H-g.denominator+1)**log_power >= 2**(h-1),
            "Funded integer carrier and preceding grid point")

    # L'(p) for p = 1-saving. This upper bound is negative uniformly on
    # [1-bit, 1]; the derivative in the saving coordinate is positive.
    lift = {7: 1, 3: 1, 5: 1, 9: -1, 4: -1, 1: -2}
    slope_at_one = sum(count * r * log(r)[int(count > 0)] for r, count in lift.items())
    curvature = sum(abs(count) * r * log(r)[1]**2 for r, count in lift.items())
    require(sum(count*r for r, count in lift.items()) == 0 and slope_at_one + bit*curvature < 0
            and min(moment(lift, s)[0] for s in (k, C)) > 0, "Directed input-lift interval")

    # Nine-stage equal-target coverage does not apply here. Hold this exact
    # mixed target invoice and all 17 native calls fixed. The most favorable
    # paid remainder concentrates its fixed rank mass at the ambient cap.
    remainder = paid.copy()
    remainder.subtract(native_paid)
    require(all(count >= 0 and r <= physical_cap for r, count in remainder.items()), "Paid remainder")
    mass = sum(r * count for r, count in remainder.items())
    relaxation = {r: target.get(r, 0) - native_paid.get(r, 0) for r in target.keys() | native_paid.keys()}
    relaxation[physical_cap] = relaxation.get(physical_cap, 0) - Q(mass, physical_cap)
    cap_lo, cap_hi = Q(".00580448601471"), Q(".00580448601473")
    require(0 < cap_lo < cap_hi < Q(1, 32)
            and moment(relaxation, cap_lo)[0] > 0 > moment(relaxation, cap_hi)[1]
            and derivative_upper(relaxation, Q(1, 32)) < 0, "Ambient fixed-profile packing bound")
    return dict(tested_margin_lower=tested, previous_margin_upper=previous,
                raw_bracket=[lo, hi], alpha_upper=enclose(alpha, alpha)[1],
                gamma_upper=enclose(gamma, gamma)[1], delta_upper=enclose(delta, delta)[1],
                input_lift_p_derivative_upper=enclose(slope_at_one+bit*curvature, slope_at_one+bit*curvature)[1],
                H=H, log_power=log_power, paid_remainder_rank_mass=mass,
                packing_raw_bracket=[cap_lo, cap_hi], fraction_of_packing_ceiling_lower=k/cap_hi,
                fraction_of_packing_ceiling_upper=k/cap_lo)
