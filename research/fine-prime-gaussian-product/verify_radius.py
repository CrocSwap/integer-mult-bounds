"""Check the absolute error guards independently of the observed coefficients."""
from fractions import Fraction as F
from math import prod


def ensure(ok, message):
    if not ok:
        raise ArithmeticError(message)


def error_profile(q, b, sizes, shifts, M):
    d = len(sizes)
    S = prod(sizes)
    gamma = sum(shifts)
    f = max(16, q + M.bit_length() + 10)
    h = F(1, 1 << q)
    hf = F(1, 1 << f)
    lam = F(1, 1 << gamma)
    middle = (24*M + 16*d + 16)*hf + 2*h
    m = 6*d*h + middle
    K = S*S << (2*b+4+3*gamma)
    forward_radius = lam/4 + m
    pointwise_radius = forward_radius**2
    error = K*(m + lam*(lam*m/2 + m*m + 2*h))
    guard = (64*d + 64)*h*K
    ensure(middle < 3*h, "the synthetic restoration exceeded the middle budget")
    ensure(F(1, 4) + 3*d*h < F(1, 2), "the middle entry could fail")
    ensure(pointwise_radius < F(1, 4), "the opposite entry could fail")
    ensure(error < guard < F(1, 2), "uncertified integer rounding")
    return middle, forward_radius, pointwise_radius, error, guard


def private_bounds(q, guard):
    G = 1 << guard
    u = F(1, 1 << (q+80*guard+32))

    def stage(node, exponent, error_exponent):
        r, e = node
        err = G**error_exponent*u*(r+1)
        return G**exponent*r + err, G**exponent*e + err

    def check(result, radius, error):
        r, e = result
        ensure(r <= radius, "stage radius exceeds its proof")
        ensure(e <= error*u, "stage error exceeds its proof")
        return result

    z = check(stage((1, 0), 3, 9), 2*G**3, 2*G**9)
    a = check(stage(z, 3, 9), 3*G**6, 5*G**12)
    b = check(stage(z, 1, 3), 3*G**4, 3*G**10)
    c = check(stage(b, 1, 16), 4*G**5, 5*G**20)
    d = check(stage(c, 1, 3), 5*G**6, 6*G**21)
    mixed = check(tuple(x+y+w for x,y,w in zip(a, b, d, strict=True)),
                  10*G**6, 7*G**21)
    tail = check(stage(mixed, 3, 9), 11*G**9, 8*G**24)
    end = check(stage(tail, 1, 3), 12*G**10, 9*G**25)
    ensure(end[1] + F(1, 1 << (q+3)) + F(2, 1 << q) < F(3, 1 << q),
           "one completed Gaussian factor can exceed its q-grid allowance")
