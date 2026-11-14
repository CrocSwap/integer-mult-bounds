# Reference kernel extracted without arithmetic edits from the independent reviewer.
# Complete source: review/independent/mechanism_check.py
# Source SHA256: fba858f2b464ad94ca1b4907647858be657e056fe1be12bdbb80fb2e023de716
#!/usr/bin/env python3
"""Independent exact challenge of the proposed R/M/E odd-coset map."""

from __future__ import annotations

import itertools
import json


H = (
    (1, 1, 1, 1),
    (1, -1, 1, -1),
    (1, 1, -1, -1),
    (1, -1, -1, 1),
)
J = (1, 1, 1, -1)
S = (1, -1, -1, 1)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def matvec(matrix, vector):
    return tuple(sum(matrix[i][j] * vector[j] for j in range(4))
                 for i in range(4))


def norm_squared(vector):
    return sum(value * value for value in vector)


def parity(vector):
    return sum(vector) & 1


def score2(twice_t, axis):
    """Twice the invariant lower-magnitude score of this coordinate pair."""
    magnitude = abs(twice_t[axis])
    require(magnitude % 2 == 1, "coordinate is not half-integral")
    if axis < 2:
        return 4 * ((magnitude - 1) // 4) + 1
    if magnitude == 1:
        return 0
    return 4 * ((magnitude - 3) // 4) + 3


def toggle_pair(twice_t):
    """The coordinate-magnitude involution M, in doubled coordinates."""
    require(len(twice_t) == 4 and all(value % 2 for value in twice_t),
            "M requires four half-integer coordinates")
    axis = min(range(4), key=lambda i: (score2(twice_t, i), i))
    result = list(twice_t)
    magnitude = abs(result[axis])
    if axis >= 2 and magnitude == 1:
        result[axis] = -result[axis]
    else:
        low = score2(twice_t, axis)
        high = low + 2
        require(magnitude in (low, high), "coordinate is outside its pair")
        sign = 1 if result[axis] > 0 else -1
        result[axis] = sign * (high if magnitude == low else low)
    return tuple(result)


def odd_map(x):
    """F(x)=E M R x for odd x; all arithmetic is integer exact."""
    require(parity(x) == 1, "odd map requires odd-total-parity input")
    dot = sum(S[i] * x[i] for i in range(4))
    require(dot % 2 == 1, "s dot x must be odd")
    twice_t = tuple(2 * x[i] - dot * S[i] for i in range(4))
    require(all(value % 2 for value in twice_t),
            "R must produce four half-integer coordinates")
    require((sum(twice_t) // 2) % 2 == 1,
            "R must produce odd coordinate sum")
    twice_m = toggle_pair(twice_t)
    require((sum(twice_m) // 2) % 2 == 0,
            "M must flip odd coordinate sum to even")
    hjm = matvec(H, twice_m)
    require(all(value % 4 == 0 for value in hjm),
            "E must produce an integer output")
    y = tuple(J[i] * (hjm[i] // 4) for i in range(4))
    require(parity(y) == 1, "E must produce odd-total-parity output")
    return y


def odd_inverse(y):
    """F^{-1}(y)=R M E^{-1} y for odd y."""
    require(parity(y) == 1, "odd inverse requires odd output")
    jy = tuple(J[i] * y[i] for i in range(4))
    twice_t = matvec(H, jy)  # t=UJy, represented as 2t.
    require(all(value % 2 for value in twice_t),
            "E inverse must produce half-integers")
    require((sum(twice_t) // 2) % 2 == 0,
            "E inverse must produce even-sum half-integers")
    twice_m = toggle_pair(twice_t)
    require((sum(twice_m) // 2) % 2 == 1,
            "M inverse step must return to odd-sum half-integers")
    dot = sum(S[i] * twice_m[i] for i in range(4))
    numerator = tuple(2 * twice_m[i] - dot * S[i] for i in range(4))
    require(all(value % 4 == 0 for value in numerator),
            "R must return integer coordinates")
    x = tuple(value // 4 for value in numerator)
    require(parity(x) == 1, "odd inverse must return odd input")
    return x


def even_map(x):
    require(parity(x) == 0, "even map requires even-total-parity input")
    hx = matvec(H, x)
    require(all(value % 2 == 0 for value in hx),
            "even input must have integral U image")
    y = tuple(value // 2 for value in hx)
    require(parity(y) == 0, "exact U must preserve even total parity")
    return y


def even_inverse(y):
    require(parity(y) == 0, "even inverse requires even output")
    hy = matvec(H, y)
    require(all(value % 2 == 0 for value in hy),
            "even output must have integral U inverse")
    return tuple(value // 2 for value in hy)


def full_map(x):
    return even_map(x) if parity(x) == 0 else odd_map(x)


def full_inverse(y):
    return even_inverse(y) if parity(y) == 0 else odd_inverse(y)



def _int4(values):
    result = tuple(values)
    if len(result) != 4 or any(type(value) is not int for value in result):
        raise ValueError("expected exactly four integers")
    return result


def hadamard_forward(values):
    """Global bijection approximating H4/2; unbounded integer coordinates."""
    return full_map(_int4(values))


def hadamard_inverse(values):
    """Exact inverse, also within unit error of H4/2."""
    return full_inverse(_int4(values))


def gaussian_forward(values):
    """Approximate C+ on (Re u, Im u, Re v, Im v); not sum preserving."""
    a, b, c, d = _int4(values)
    y = full_map((a, -b, c, d))
    return y[0], y[3], y[1], -y[2]


def gaussian_inverse(values):
    """Exact inverse of gaussian_forward; approximates C- explicitly."""
    a, b, c, d = _int4(values)
    y = full_inverse((a, c, -d, b))
    return y[0], -y[1], y[2], y[3]
