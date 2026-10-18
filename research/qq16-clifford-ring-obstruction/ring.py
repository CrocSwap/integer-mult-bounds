"""Exact D[zeta_8] arithmetic and its F25 specialization; no floats."""
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def neg(a):
    return tuple(-x for x in a)


def mul(a, b):
    out = [Q(0)] * 4
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[(i + j) % 4] += x * y * (-1 if i + j >= 4 else 1)
    return tuple(out)


def scalar(value):
    return (Q(value), Q(0), Q(0), Q(0))


ZERO, ONE = scalar(0), scalar(1)
ZETA = (Q(0), Q(1), Q(0), Q(0))
I = mul(ZETA, ZETA)
ZETA3 = mul(I, ZETA)
SQRT2 = add(ZETA, neg(ZETA3))
HALFROOT = mul(scalar(Q(1, 2)), SQRT2)


def fmul(a, b, square=2):
    return ((a[0]*b[0] + square*a[1]*b[1]) % 5,
            (a[0]*b[1] + a[1]*b[0]) % 5)


def dyadic(value):
    return value.denominator & (value.denominator - 1) == 0


def reduce(value):
    need(len(value) == 4 and all(dyadic(v) for v in value),
         "dyadic coefficient required")
    c = [v.numerator * pow(v.denominator, -1, 5) % 5 for v in value]
    return ((c[0] + 2*c[2]) % 5, (4*c[1] + 3*c[3]) % 5)


def gate(values, operation, bit, other=None, inverse=False, normalizer=HALFROOT):
    """Literal fixed three-bit gate, acting on eight coefficient rows."""
    need(len(values) == 8 and bit in range(3), "three-bit gate domain")
    need(operation in ('H', 'S', 'T', 'X', 'Z', 'CNOT', 'SWAP'), "gate name")
    values = values[:]
    if operation == 'H':
        for j in range(8):
            if not j >> bit & 1:
                k = j ^ (1 << bit)
                a, b = values[j], values[k]
                values[j] = mul(normalizer, add(a, b))
                values[k] = mul(normalizer, add(a, neg(b)))
    elif operation in ('T', 'S', 'Z'):
        phase = {'T': ZETA, 'S': I, 'Z': scalar(-1)}[operation]
        if inverse:
            phase = {'T': neg(ZETA3), 'S': neg(I), 'Z': scalar(-1)}[operation]
        values = [mul(phase, v) if j >> bit & 1 else v for j, v in enumerate(values)]
    else:
        need(operation == 'X' or other in range(3) and other != bit,
             "distinct controlled/permuted bits")
        out = [ZERO] * 8
        for j, v in enumerate(values):
            if operation == 'SWAP':
                k = j ^ ((1 << bit) | (1 << other)) if ((j >> bit) ^ (j >> other)) & 1 else j
            else:
                k = j ^ (1 << bit) if operation == 'X' or j >> other & 1 else j
            out[k] = v
        values = out
    return values
