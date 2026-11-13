#!/usr/bin/env python3
"""Exact finite conformance for the two-coordinate Euclidean envelope."""

from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(rho, beta):
    for value in (rho, beta):
        require(type(value) is F, "parameters must be Fractions")
        require(max(abs(value.numerator).bit_length(),
                    value.denominator.bit_length()) <= 256, "parameter height")
    require(0 < rho < 1 and beta >= 1, "parameter domain")


def envelope(rho, beta):
    """Return A,B,D with the exact squared optimum A+B*sqrt(D)."""
    parameters(rho, beta)
    c = min(beta - 1, F(1))
    t = rho * c / (1 - rho + rho * c)
    scale = 1 / (1 - rho) ** 2
    return scale * (1 - t + t * t), scale * t, t * t - 2 * t + 2


def attainer(rho, beta):
    parameters(rho, beta)
    c = min(beta - 1, F(1))
    return ((rho, F(0)), (rho * c, rho * (1 - c)))


def nonnegative(a, b, d):
    """Exact sign test for a+b*sqrt(d), with rational a,b and d>=0."""
    require(d >= 0, "negative radicand")
    if b == 0 or d == 0:
        return a >= 0
    if a >= 0 and b >= 0:
        return True
    if a <= 0 and b <= 0:
        return a == b == 0
    if a >= 0:
        return a * a >= b * b * d
    return b * b * d >= a * a


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def neg(x):
    return (-x[0], -x[1])


def mul(x, y):
    return (x[0] * y[0] - x[1] * y[1],
            x[0] * y[1] + x[1] * y[0])


def conj(x):
    return (x[0], -x[1])


def norm2(x):
    return x[0] * x[0] + x[1] * x[1]


def reciprocal(x):
    n = norm2(x)
    require(n > 0, "singular inverse")
    return (x[0] / n, -x[1] / n)


def real_matrix(a):
    return tuple(tuple((x, F(0)) for x in row) for row in a)


def matmul(a, b):
    return tuple(tuple(add(mul(a[i][0], b[0][j]),
                           mul(a[i][1], b[1][j])) for j in range(2))
                 for i in range(2))


def inverse(a):
    d = reciprocal(add(mul(a[0][0], a[1][1]),
                       neg(mul(a[0][1], a[1][0]))))
    out = ((mul(a[1][1], d), mul(neg(a[0][1]), d)),
           (mul(neg(a[1][0]), d), mul(a[0][0], d)))
    ident = real_matrix(((F(1), F(0)), (F(0), F(1))))
    require(matmul(a, out) == ident, "right inverse")
    require(matmul(out, a) == ident, "left inverse")
    return out


def resolvent(e):
    a = tuple(tuple(add((F(i == j), F(0)), neg(e[i][j]))
                    for j in range(2)) for i in range(2))
    return inverse(a)


def gram(r):
    h00 = norm2(r[0][0]) + norm2(r[1][0])
    h11 = norm2(r[0][1]) + norm2(r[1][1])
    h01 = add(mul(conj(r[0][0]), r[0][1]),
              mul(conj(r[1][0]), r[1][1]))
    return h00, h11, h00 * h11 - norm2(h01)


def bound_check(e, rho, beta, attained=False):
    a, b, d = envelope(rho, beta)
    h00, h11, det = gram(resolvent(e))
    require(nonnegative(a - h00, b, d), "first PSD minor")
    require(nonnegative(a - h11, b, d), "second PSD minor")
    u = a * a + b * b * d - (h00 + h11) * a + det
    v = 2 * a * b - (h00 + h11) * b
    require(nonnegative(u, v, d), "determinant PSD minor")
    if attained:
        require(u == v == 0, "attaining eigenvalue")


def admitted_units(a, units, beta):
    return all(sum(row) <= units for row in a) and all(
        sum(a[i][j] for i in range(2)) <= beta * units for j in range(2))


def saturate(a, rho, beta):
    out = [list(row) for row in a]
    for i in range(2):
        deficit = rho - sum(out[i])
        for j in range(2):
            room = beta * rho - sum(out[k][j] for k in range(2))
            delta = min(deficit, room)
            require(delta >= 0, "completion capacity")
            out[i][j] += delta
            deficit -= delta
        require(deficit == 0, "completion row")
    require(all(out[i][j] >= a[i][j] for i in range(2) for j in range(2)),
            "completion domination")
    return tuple(tuple(row) for row in out)


def reduction_check(a, rho, beta):
    completed = saturate(a, rho, beta)
    r, old = resolvent(real_matrix(completed)), resolvent(real_matrix(a))
    require(all(r[i][j][0] >= old[i][j][0]
                for i in range(2) for j in range(2)), "inverse domination")
    p = tuple(tuple(x / rho for x in row) for row in completed)
    if p[0][0] + p[1][0] < 1:
        p = tuple(tuple(p[1-i][1-j] for j in range(2)) for i in range(2))
    s, delta = p[0][0] + p[1][0] - 1, p[0][0] - p[1][0]
    require(0 <= s <= min(beta - 1, 1) and abs(delta) <= 1 - s,
            "stochastic polygon")
    q = real_matrix(((F(1), F(1)), (F(1), F(-1))))
    rp = resolvent(real_matrix(tuple(tuple(rho*x for x in row) for row in p)))
    rotated = matmul(matmul(q, rp), q)
    alpha, z = 1 / (1 - rho), 1 / (1 - rho * delta)
    expected = real_matrix(((2 * alpha, 2 * alpha * rho * s * z),
                            (F(0), 2 * z)))
    require(rotated == expected, "orthogonal-coordinate formula")


def rational_grid():
    count = 0
    rows = tuple((a, b) for a in range(5) for b in range(5-a))
    for rho, beta in product((F(1,5), F(1,2), F(3,4), F(9,10)),
                             (F(1), F(5,4), F(3,2), F(7,4), F(2), F(3))):
        for a in product(rows, repeat=2):
            if admitted_units(a, 4, beta):
                e = tuple(tuple(rho*x/4 for x in row) for row in a)
                bound_check(real_matrix(e), rho, beta)
                reduction_check(e, rho, beta)
                count += 1
    return count


def phase_grid():
    count = 0
    phases = ((1, 0), (-1, 0), (0, 1), (0, -1))
    rows = tuple((a, b) for a in range(3) for b in range(3-a))
    for beta, a in product((F(1), F(3,2), F(2)), product(rows, repeat=2)):
        if not admitted_units(a, 2, beta):
            continue
        choices = tuple(phases if x else ((1, 0),) for row in a for x in row)
        for phase in product(*choices):
            e = tuple(tuple((F(a[i][j] * phase[2*i+j][0], 4),
                             F(a[i][j] * phase[2*i+j][1], 4))
                            for j in range(2)) for i in range(2))
            bound_check(e, F(1,2), beta)
            count += 1
    return count


def sharpness_grid():
    count = 0
    for denominator in range(2, 13):
        for numerator, k in product(range(1, denominator), range(4, 13)):
            rho, beta = F(numerator, denominator), F(k, 4)
            e = attainer(rho, beta)
            require(all(sum(row) == rho for row in e), "attainer row cap")
            require(all(sum(e[i][j] for i in range(2)) <= beta * rho
                        for j in range(2)), "attainer column cap")
            bound_check(real_matrix(e), rho, beta, attained=True)
            count += 1
    return count


def controls():
    bad = ((F(0), F(1)), (F(1), F(1)), (F(-1), F(2)),
           (F(2), F(2)), (F(1,2), F(3,4)), (True, F(2)),
           (0.5, F(2)), (F(1,2), 2), (F(1, 2**257), F(2)))
    for rho, beta in bad:
        try:
            envelope(rho, beta)
        except ValueError:
            continue
        raise ValueError("invalid parameter accepted")
    require(envelope(F(1,2), F(1))[:2] == (F(4), F(0)), "balanced cap")
    require(envelope(F(1,2), F(2)) == envelope(F(1,2), F(100)), "redundant cap")
    require(envelope(F(1,2), F(3,2)) == (F(28,9), F(4,3), F(13,9)),
            "worked example")
    require(not nonnegative(F(-2), F(1), F(3)), "negative surd")
    require(nonnegative(F(2), F(-1), F(3)), "positive surd")
    require(nonnegative(F(-2), F(1), F(4)), "zero surd")
    require(not nonnegative(F(0), F(-1), F(3)), "pure negative surd")
    return len(bad) + 7


def main():
    counts = {"rational_cap_cases": rational_grid(),
              "gaussian_rational_cap_cases": phase_grid(),
              "attaining_parameter_presentations": sharpness_grid(),
              "controls": controls()}
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        with (root / name).open("rb") as source:
            raw = source.read(1024 * 1024 + 1)
        require(len(raw) <= 1024 * 1024, "receipt input size")
        hashes[name] = sha256(raw).hexdigest()
    print(json.dumps({"status": "PASS_TWO_COORDINATE_EUCLIDEAN_RESOLVENT",
                      "counts": counts, "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
