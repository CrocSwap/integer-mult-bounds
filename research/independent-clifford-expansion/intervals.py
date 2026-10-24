"""Outward integer intervals for the finite concave-power certificate.

No floating arithmetic is used. Apache-2.0, OpenAI Codex assistance.
"""
from fractions import Fraction as Q

BITS = 128
SCALE = 1 << BITS


def updiv(a, b):
    return -(-a // b)


def rational_bounds(q):
    return q.numerator*SCALE//q.denominator, updiv(q.numerator*SCALE, q.denominator)


def log_bounds(r):
    def series(q):
        z = (q-1)/(q+1)
        low = 2*sum((z**(2*k+1)/Q(2*k+1) for k in range(48)), Q(0))
        tail = 2*z**97/(97*(1-z*z))
        return low, low+tail
    k = r.bit_length()-1
    a, b = series(Q(2))
    c, d = series(Q(r, 1 << k))
    return rational_bounds(k*a+c)[0], rational_bounds(k*b+d)[1]


LOGS = {r: log_bounds(r) for r in range(1, 10)}


def power_bounds(r, c):
    """Bounds scaled by SCALE for r**(1-c), 0<=c<=1/200."""
    if r == 1:
        return SCALE, SCALE
    lo, hi = LOGS[r]
    xlo = lo*c.numerator//c.denominator
    xhi = updiv(hi*c.numerator, c.denominator)
    # exp(x), x=c*log(r)<1/2. All terms are positive. The omitted
    # tail is at most twice its first term, since its ratios are <1/2.
    tlo = thi = total_lo = total_hi = SCALE
    for k in range(1, 19):
        tlo = tlo*xlo//(SCALE*k)
        thi = updiv(thi*xhi, SCALE*k)
        total_lo += tlo
        total_hi += thi
    next_hi = updiv(thi*xhi, SCALE*19)
    total_hi += 2*next_hi
    return r*SCALE*SCALE//total_hi, updiv(r*SCALE*SCALE, total_lo)


def dominance(delta):
    return [sum(delta[r]*min(r,k) for r in range(1,10)) for k in range(1,10)]


def certify(patterns):
    """Certify each signed rank polynomial nonnegative on 0<=C<=.005.

    Concave dominance covers most patterns for every increasing concave
    function vanishing at zero. The rest use outward moment or derivative
    bounds. A zero rank-mass polynomial starts at zero; a positive lower
    derivative proves it stays nonnegative. No sampled signs are accepted.
    """
    remaining = []
    dominant = 0
    for p in patterns:
        d = p['delta']
        if min(dominance(d)) >= 0:
            dominant += 1
        else:
            mass = sum(r*d[r] for r in range(1,10))
            if mass < 0:
                raise ValueError('a true rank-mass improvement requires investigation')
            remaining.append((d, mass))
    for pieces in (8,16,32,64,128,256,512,1024,2048):
        powers = [{r: power_bounds(r, Q(i,200*pieces)) for r in range(1,10)}
                  for i in range(pieces+1)]
        bounds = []
        for delta, mass in remaining:
            least = None
            for i in range(pieces):
                lower = 0
                for r in range(1,10):
                    if mass == 0:
                        coefficient = -delta[r]
                        a = powers[i+1][r][0]*LOGS[r][0]//SCALE
                        b = updiv(powers[i][r][1]*LOGS[r][1], SCALE)
                    else:
                        coefficient = delta[r]
                        a, b = powers[i+1][r][0], powers[i][r][1]
                    lower += coefficient*(a if coefficient >= 0 else b)
                least = lower if least is None else min(least,lower)
            bounds.append(least)
        if all(b > 0 for b in bounds):
            return dict(interval_C=['0','1/200'], fixed_point_bits=BITS,
                        concave_dominance_patterns=dominant,
                        interval_patterns=len(remaining), subdivisions=pieces,
                        minimum_scaled_lower_bound=min(bounds) if bounds else None,
                        zero_mass_patterns=sum(m == 0 for _,m in remaining),
                        scale=str(SCALE))
    raise ValueError('interval certificate failed; do not infer local optimality')
