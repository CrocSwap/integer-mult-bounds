"""Coarse-grid source restoration; exact rational reference implementation.

The mutable source and target already own working-precision words. Unused low
source bits are known zeros, not arbitrary borrowed dirt. No full-array scratch
is allocated by execute. Coefficients/phases and their access are supplied.
"""
from fractions import Fraction as F

ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b): return a[0] + b[0], a[1] + b[1]
def sub(a, b): return a[0] - b[0], a[1] - b[1]
def mul(a, b): return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]
def conj(a): return a[0], -a[1]
def norm2(a): return a[0]*a[0]+a[1]*a[1]
def l1(a): return abs(a[0])+abs(a[1])


def div(a, b):
    d = norm2(b)
    need(d > 0, 'zero divisor')
    z = mul(a, conj(b))
    return z[0]/d, z[1]/d


def rnd(a, bits):
    scale = 1 << bits
    def component(v):
        z = v*scale+F(1, 2)
        return F(z.numerator//z.denominator, scale)
    return component(a[0]), component(a[1])


def indices(length, direction):
    return range(length) if direction == 1 else range(length-1, -1, -1)


def inverse_scan(x, coefficient, beta, bits, direction):
    """Two scans, overwriting only on the second; O(1) scalar state."""
    z, power = ZERO, ONE
    for i in indices(len(x), direction):
        b = coefficient(i)
        z = rnd(add(x[i], mul(b, z)), bits)
        power = rnd(mul(b, power), bits)
    den = sub(ONE, power)
    need(norm2(den) >= (beta/2)**2, 'closure denominator')
    previous = rnd(div(z, den), bits)
    for i in indices(len(x), direction):
        previous = rnd(add(x[i], mul(coefficient(i), previous)), bits)
        x[i] = previous


def inverse_factor(x, factor, bits):
    rho, beta, phase, direction = factor
    n = len(x)
    if norm2(rho) < 1:
        # (W-rho)^-1 = W^-1 (I-rho W^-1)^-1.
        coefficient = lambda i: mul(rho, conj(phase((i+direction) % n)))
        inverse_scan(x, coefficient, beta, bits, -direction)
        first_index = 0 if direction == 1 else n-1
        first = x[first_index]
        for i in indices(n, direction):
            j = (i+direction) % n
            v = first if j == first_index else x[j]
            x[i] = rnd(mul(conj(phase(j)), v), bits)
    else:
        b = div(ONE, rho)
        inverse_scan(x, lambda i: mul(b, phase(i)), beta, bits, direction)
        minus_b = (-b[0], -b[1])
        for i in range(n):
            x[i] = rnd(mul(minus_b, x[i]), bits)


def forward_factor(x, factor, bits, wrong_seam=False):
    rho, _, phase, direction = factor
    previous = ZERO if wrong_seam else x[-1 if direction == 1 else 0]
    for i in indices(len(x), direction):
        original = x[i]
        x[i] = rnd(sub(mul(phase(i), previous), mul(rho, original)), bits)
        previous = original


def budgets(factors, scale, bound, bits):
    """All-length modulus bounds, including forward source restoration."""
    u = F(1, 1 << bits)
    amplification, error = F(scale), F(0)
    rows = []
    for rho, beta, _, _ in factors:
        need(u <= beta*beta/2, 'closure precision')
        # First-order inverse + rounded unit shift or outer scalar.
        error = error/beta+7*(amplification*bound+error+1)*u/beta**3
        amplification /= beta
        rows.append((amplification*bound, error))
    recovery = error
    for rho, _, _, _ in reversed(factors):
        recovery = (1+l1(rho))*recovery+u
    recovery = recovery/scale+u
    return error, recovery, rows


def working_bits(factors, scale, bound, coarse_bits, target_bits):
    bits = max(coarse_bits, target_bits)
    while True:
        if all(F(1, 1 << bits) <= beta*beta/2 for _, beta, _, _ in factors):
            error, recovery, _ = budgets(factors, scale, bound, bits)
            if error <= F(1, 1 << target_bits) and recovery < F(1, 1 << (coarse_bits+1)):
                return bits
        bits += 1


def validate(x, y, factors, scale, bound, coarse_bits, bits, target_bits):
    need(x is not y, 'source/target alias')
    need(len(x) > 0 and len(y) == len(x), 'array length')
    need(type(scale) is int and scale > 0, 'positive integral scale')
    need(type(coarse_bits) is int and 0 <= coarse_bits <= bits, 'coarse precision')
    need(type(target_bits) is int and target_bits > 0, 'target precision')
    need(bound >= 0, 'source bound')
    need(all(v == rnd(v, coarse_bits) for v in x), 'source coarse grid')
    need(all(v == rnd(v, bits) for v in y), 'target working grid')
    need(all(norm2(v) <= bound*bound for v in x), 'source magnitude')
    for rho, beta, phase, direction in factors:
        need(direction in (-1, 1), 'direction')
        b = rho if norm2(rho) < 1 else div(ONE, rho)
        need(0 < beta <= 1 and norm2(b) <= (1-beta)**2, 'stable root')
        need(all(norm2(phase(i)) == 1 for i in range(len(x))), 'unit phase')
    error, recovery, _ = budgets(factors, scale, bound, bits)
    need(error <= F(1, 1 << target_bits), 'target budget')
    need(recovery < F(1, 1 << (coarse_bits+1)), 'recovery budget')
    return error, recovery


def execute(x, y, factors, scale, bound, coarse_bits, bits, target_bits,
            *, validate_inputs=True, wrong_seam=False, round_coarse=True,
            wrong_restore_order=False):
    if validate_inputs:
        validate(x, y, factors, scale, bound, coarse_bits, bits, target_bits)
    for i in range(len(x)):
        x[i] = (x[i][0]*scale, x[i][1]*scale)
    for factor in factors:
        inverse_factor(x, factor, bits)
    for i in range(len(x)):
        y[i] = add(y[i], x[i])  # exact working-grid integer addition
    order = factors if wrong_restore_order else reversed(factors)
    for factor in order:
        forward_factor(x, factor, bits, wrong_seam)
    for i in range(len(x)):
        x[i] = rnd((x[i][0]/scale, x[i][1]/scale), bits)
        if round_coarse:
            x[i] = rnd(x[i], coarse_bits)
