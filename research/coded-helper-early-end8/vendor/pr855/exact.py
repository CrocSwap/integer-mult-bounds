"""Check the finite packing certificate using rational arithmetic only.

The recorded potentials are witnesses, not trusted solver output. Every edge
inequality and every mixture is checked again. See README.md for the proof.
"""
from fractions import Fraction as Q
from functools import lru_cache

SCALE = 10**30
POTENTIAL_SCALE = 10**16
MODULUS = 37
CAPACITY_SCORE = {8: 6, 16: 12, 32: 24, 48: 37}
WIDTH_SCORE = {4: 3, 5: 3, 7: 5, 8: 6, 9: 7}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def log_interval(z):
    """Bound log((1+z)/(1-z)) by 48 terms and a geometric tail."""
    require(0 <= z <= Q(1, 3), "log argument outside certified range")
    value, power = Q(0), z
    for j in range(48):
        value += 2 * power / (2*j + 1)
        power *= z*z
    return value, value + 2*power / (97*(1-z*z))


@lru_cache(None)
def power_bounds(r, b):
    """Outward-rounded integer bounds for SCALE * r**(1-b)."""
    require(type(r) is int and r >= 0 and 0 < b < 1, "power domain")
    if r in (0, 1):
        return r*SCALE, r*SCALE
    k = r.bit_length() - 1
    l2, u2 = log_interval(Q(1, 3))
    m = Q(r, 2**k)
    lm, um = log_interval((m-1)/(m+1))
    lo, hi = b*(k*l2+lm), b*(k*u2+um)
    require(0 < lo <= hi < 1, "exp argument outside certified range")

    def alternating(x):
        term = total = Q(1)
        for n in range(1, 21):
            term *= -x/n
            total += term
        # Decreasing terms on [0,1]: degree 21 is below, degree 20 above.
        return total + term*(-x)/21, total

    lower = r*alternating(hi)[0]*SCALE
    upper = r*alternating(lo)[1]*SCALE
    return lower.numerator//lower.denominator, -(-upper.numerator//upper.denominator)


def patterns():
    """All integer width multisets fitting one capacity, including empty."""
    widths = sorted(WIDTH_SCORE)
    result = []

    def visit(capacity, j, used, multiplicities):
        if j == len(widths):
            score = CAPACITY_SCORE[capacity] - sum(
                WIDTH_SCORE[w]*n for w, n in zip(widths, multiplicities))
            result.append((capacity, capacity-used, tuple(multiplicities), score))
            return
        for n in range((capacity-used)//widths[j] + 1):
            visit(capacity, j+1, used+n*widths[j], multiplicities+[n])

    for capacity in sorted(CAPACITY_SCORE):
        visit(capacity, 0, 0, [])
    return result


def shifted(base, positive, negative, deltas):
    keys = set(base) | set(deltas['positive']) | set(deltas['negative'])
    result = {r: base.get(r, 0) + positive*deltas['positive'].get(r, 0)
              + negative*deltas['negative'].get(r, 0) for r in keys}
    require(all(type(n) is int and n >= 0 for n in result.values()),
            "invalid mixture inventory")
    return {r: n for r, n in result.items() if n}


def verify(model, certificate, check_record=True):
    b = Q(model['endpoint'])
    require(Q(certificate['endpoint']) == b, "endpoint mismatch")
    require(set(model['capacities']) == set(CAPACITY_SCORE), "capacity domain")
    require(set(model['widths']) == set(WIDTH_SCORE), "width domain")
    require(certificate['potential_scale'] == POTENTIAL_SCALE, "potential scale")
    lam = certificate['lambda_units_1e30']
    d = certificate['potentials']
    require(type(lam) is int and lam < 0, "lambda must be a negative integer")
    require(len(d) == MODULUS and all(type(x) is int for x in d) and d[0] == 0,
            "potential domain or origin")
    pats = patterns()
    require(len(pats) == 1163, "pattern enumeration changed")
    phi = {r: power_bounds(r, b)[0] - r*SCALE for r in range(49)}
    potential_unit = SCALE//POTENTIAL_SCALE
    for capacity, residual, counts, score in pats:
        require(score >= 0, "negative pattern score")
        gap = phi[residual] - lam*score
        require(gap >= 0, f"pattern dual inequality: {capacity}, {counts}")
    for capacity, residual, counts, score in pats:
        gap = phi[residual] - lam*score
        for j in range(MODULUS):
            require((d[(j+score) % MODULUS]-d[j])*potential_unit <= gap,
                    f"potential inequality: residue {j}, capacity {capacity}, {counts}")

    # A positive control: the inherited profile really meets its own endpoint.
    threshold_lo, threshold_hi = [model['live']*x for x in power_bounds(model['m'], b)]
    baseline_hi = sum(n*power_bounds(r, b)[1] for r, n in model['global'].items())
    require(baseline_hi < threshold_lo, "baseline endpoint positive control")

    capacity_mass = sum(c*n for c, n in model['capacities'].items())
    capacity_score = sum(CAPACITY_SCORE[c]*n for c, n in model['capacities'].items())
    rows = []
    for positive in range(model['calls']+1):
        for negative in range(model['calls']-positive+1):
            if positive + negative == 0:
                continue
            local = shifted(model['local'], positive, negative, model['profile_deltas'])
            widths = shifted(model['widths'], positive, negative, model['width_deltas'])
            require(set(local) <= set(range(1, 49)) and set(widths) <= set(WIDTH_SCORE),
                    "mixture uses an uncertified rank or width")
            idle_mass = capacity_mass - sum(w*n for w, n in widths.items())
            score = capacity_score - sum(WIDTH_SCORE[w]*n for w, n in widths.items())
            require(idle_mass >= 0 and score >= 0, "mixture mass or score")
            require(sum(r*n for r, n in local.items()) + idle_mass == model['rank_mass'],
                    "local/idle rank conservation")
            lower = (sum(n*power_bounds(r, b)[0] for r, n in local.items())
                     + idle_mass*SCALE + lam*score + d[score % MODULUS]*potential_unit)
            margin = lower-threshold_hi
            require(margin > 0, f"budget inequality: positive={positive}, negative={negative}")
            rows.append((margin, positive, negative))
    margin, positive, negative = min(rows)
    summary = {
        'endpoint': str(b), 'patterns': len(pats),
        'potential_inequalities': MODULUS*len(pats), 'mixtures': len(rows),
        'lambda_units_1e30': lam, 'potential_scale': POTENTIAL_SCALE, 'potentials': d,
        'minimum_margin_units_1e30': margin,
        'minimum_at': {'positive': positive, 'negative': negative},
        'minimum_margin_greater_than': str(Q(margin//10**18, 10**12)),
    }
    if check_record:
        require(summary == certificate, "recorded exact-certificate summary differs")
    return summary


def controls(model, certificate):
    from copy import deepcopy

    cases = []
    bad = deepcopy(certificate)
    bad['lambda_units_1e30'] += 10**24  # Raise lambda by 10^-6.
    cases.append(('raise_lambda', bad, 'pattern dual inequality'))
    bad = deepcopy(certificate)
    bad['potentials'][22] += 1000
    cases.append(('raise_residue_22', bad, 'potential inequality'))
    bad = deepcopy(certificate)
    bad['potentials'] = [0]*MODULUS
    # Zero potentials satisfy the edges, but cannot exclude the one-call case.
    cases.append(('omit_integer_correction', bad, 'budget inequality: positive=0, negative=1'))
    rejected = {}
    for name, bad, expected in cases:
        try:
            verify(model, bad, check_record=False)
        except ValueError as error:
            require(expected in str(error), f"wrong failure for {name}: {error}")
            rejected[name] = str(error)
        else:
            raise ValueError(f"negative control accepted: {name}")
    return rejected
