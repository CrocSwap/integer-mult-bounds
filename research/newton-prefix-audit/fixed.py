"""Integer-significand port of the retained Section 09 equations.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
No Fraction, floating-point, divmod oracle, or square-root oracle is used here.
"""


def demand(ok, message):
    if not ok:
        raise ValueError(message)


def floor_shift(value, bits):
    return value >> bits if bits >= 0 else value << -bits


def working_steps(p, guard=5, warmup=True):
    demand(type(p) is int and p >= 1, "positive integer target required")
    if warmup:
        yield 1, 6
    achieved = 1
    while achieved < p:
        achieved = min(2 * achieved, p)
        yield achieved, achieved + guard


def prefix(numerator, bits, t, stale=None):
    if stale is not None and t > stale:
        return floor_shift(numerator, bits - stale) << (t - stale)
    return floor_shift(numerator, bits - t)


def reciprocal(cn, cb, p, *, guard=5, warmup=True, stale=None):
    demand(type(cb) is int and cb >= 0, "nonnegative input scale required")
    demand((1 << cb) <= cn < (2 << cb), "reciprocal normalization")
    xn, xb = 5, 3
    trace = []
    for m, t in working_steps(p, guard, warmup):
        ct = prefix(cn, cb, t, stale)
        u = floor_shift(ct * xn, xb)
        nxt = floor_shift(xn * ((2 << t) - u), xb)
        trace.append((m, t, ct, u, nxt))
        xn, xb = nxt, t
    return xn, xb, tuple(trace)


def square_root(cn, cb, p, *, guard=5, warmup=True, stale=None,
                normalization_offset=0):
    demand(type(cb) is int and cb >= 0, "nonnegative input scale required")
    demand((1 << cb) <= cn < (4 << cb), "root normalization")
    xn, xb = 3, 1
    trace = []
    for m, t in working_steps(p, guard, warmup):
        ct = prefix(cn, cb, t, stale)
        db = xn.bit_length() - 1
        j = db - xb
        zn, zb, inner = reciprocal(xn, db, t)
        qt = floor_shift(ct * zn, zb + j + normalization_offset)
        nxt = floor_shift((xn << t) + (qt << xb), xb + 1)
        trace.append((m, t, ct, j, zn, zb, qt, nxt, inner))
        xn, xb = nxt, t
    return xn, xb, tuple(trace)


def correct_division(a, b, q0, *, low=True, high=True):
    r = a - b * q0
    q = q0
    if low and r < 0:
        q -= 1
        r += b
    if high and r >= b:
        q += 1
        r -= b
    return q, r


def correct_root(a, q0, *, low=True, high=True):
    q = q0
    if low and q * q > a:
        q -= 1
    if high and (q + 1) * (q + 1) <= a:
        q += 1
    return q


def divide(a, b, n, prepared=None):
    demand(type(n) is int and n >= 1, "positive supplied width required")
    demand(0 <= a < (1 << n) and 0 < b < (1 << n), "division input range")
    if a == 0:
        return 0, 0, 0
    h = b.bit_length() - 1
    xn, xb, _ = prepared if prepared is not None else reciprocal(b, h, 2 * n + 4)
    q0 = floor_shift(a * xn, xb + h)
    q, r = correct_division(a, b, q0)
    return q, r, q0


def integer_root(a, n):
    demand(type(n) is int and n >= 1, "positive supplied width required")
    demand(0 <= a < (1 << n), "root input range")
    if a == 0:
        return 0, 0
    e = (a.bit_length() - 1) // 2
    xn, xb, _ = square_root(a, 2 * e, 2 * n + 4)
    q0 = floor_shift(xn, xb - e)
    return correct_root(a, q0), q0
