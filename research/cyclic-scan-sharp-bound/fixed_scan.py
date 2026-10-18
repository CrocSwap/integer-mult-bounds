"""Integer-grid reference for the sharp periodic-scan rounding lemma.

Apache-2.0. Substantial OpenAI Codex assistance; see README.md.
Only stored grid numerators are propagated. Coefficients remain exact rationals.
"""
from fractions import Fraction as F


def require(ok, message):
    if not ok:
        raise ValueError(message)


def nearest(v):
    """Nearest integer, with half-integers rounded toward positive infinity."""
    v = F(v) + F(1, 2)
    return v.numerator // v.denominator


def run(x, coefficients, beta, bits, direction=1, mutation=None):
    n = len(x)
    require(n > 0 and len(coefficients) == n, "coefficient length")
    require(direction in (-1, 1), "direction")
    require(type(bits) is int and bits >= 0, "precision")
    require(0 < beta <= 1, "margin")
    require(all(a*a+b*b <= (1-beta)**2 for a, b in coefficients), "stability")
    scale = 1 << bits
    require(F(1, scale) <= beta / 2, "closure precision")
    order = range(n) if direction == 1 else range(n-1, -1, -1)

    def update(value, coefficient, offset=(0, 0)):
        a, b = coefficient
        v, w = value
        return (nearest(a*v-b*w+scale*offset[0]),
                nearest(a*w+b*v+scale*offset[1]))

    z, power = (0, 0), (scale, 0)
    for i in order:
        z = update(z, coefficients[i], x[i])
        power = update(power, coefficients[i])
    sign = -1 if mutation != "plus_denominator" else 1
    den = (scale+sign*power[0], sign*power[1])
    den_norm = den[0]**2 + den[1]**2
    require(den_norm > 0, "closure denominator")
    seed = (nearest(F(scale*(z[0]*den[0]+z[1]*den[1]), den_norm)),
            nearest(F(scale*(z[1]*den[0]-z[0]*den[1]), den_norm)))
    if mutation == "zero_seed":
        seed = (0, 0)
    output, previous = [(0, 0)]*n, seed
    for i in order:
        coefficient = coefficients[i if mutation != "constant_coefficient" else 0]
        previous = update(previous, coefficient, x[i])
        output[i] = previous
    return [(F(a, scale), F(b, scale)) for a, b in output]


def error_bound(B, beta, bits):
    """The non-simplified universal bound from PROOF.md."""
    return F(1, 1 << bits) * (2*B/beta**2 + 3/beta + 1)
