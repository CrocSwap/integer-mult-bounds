#!/usr/bin/env python3
"""Finite checks for the all-old-once three-frame character proof.

The case analysis lives in PROOF.md. This program checks the polynomial
identity used for the scale formula, the mod-8 discriminant lemma, and
explicit characters on a declared finite fixture list.
"""

from collections import Counter
from fractions import Fraction
import math


def egcd(a, b):
    if b == 0:
        if a == 0:
            return 0, 1, 0
        sign = 1 if a > 0 else -1
        return abs(a), sign, 0
    g, x, y = egcd(b, a % b)
    return g, y, x - (a // b) * y


def bezout(coeffs):
    g = 0
    coef = [0] * len(coeffs)
    for i, value in enumerate(coeffs):
        g2, x, y = egcd(g, value)
        coef = [c * x for c in coef]
        coef[i] += y
        g = g2
    return g, coef


def kernel_row(row):
    n = len(row)
    transform = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    reduced = list(row)
    pivot = next((i for i in range(n) if reduced[i] != 0), None)
    if pivot is None:
        return [[transform[k][j] for k in range(n)] for j in range(n)]
    if pivot != 0:
        for k in range(n):
            transform[k][0], transform[k][pivot] = transform[k][pivot], transform[k][0]
        reduced[0], reduced[pivot] = reduced[pivot], reduced[0]
    for i in range(1, n):
        if reduced[i] == 0:
            continue
        g, s, t = egcd(reduced[0], reduced[i])
        old0, oldi = reduced[0], reduced[i]
        new0 = [s * transform[k][0] + t * transform[k][i] for k in range(n)]
        newi = [(oldi // g) * transform[k][0] - (old0 // g) * transform[k][i] for k in range(n)]
        for k in range(n):
            transform[k][0] = new0[k]
            transform[k][i] = newi[k]
        reduced[0] = g
        reduced[i] = 0
    return [[transform[k][j] for k in range(n)] for j in range(1, n)]


def solve_one(coeffs, target):
    g, coef = bezout(list(coeffs))
    if target % g:
        return None
    scale = target // g
    return [c * scale for c in coef]


def solve_two(c1, t1, c2, t2, modulus):
    particular4 = solve_one(list(c1) + [-modulus], t1)
    if particular4 is None:
        return None
    point = particular4[:3]
    generators = [vector[:3] for vector in kernel_row(list(c1) + [-modulus])]
    rhs = t2 - sum(c2[i] * point[i] for i in range(3))
    columns = [sum(c2[i] * gen[i] for i in range(3)) for gen in generators]
    coeffs = solve_one(columns + [-modulus], rhs)
    if coeffs is None:
        return None
    solution = point[:]
    for weight, gen in zip(coeffs, generators):
        for i in range(3):
            solution[i] += weight * gen[i]
    return solution


def dot(p, q):
    return p[0] * q[0] + p[1] * q[1]


def delta(p, q):
    return p[0] * q[1] - p[1] * q[0]


def coefficient(direction, scale):
    x, y = direction
    return tuple(scale * value for value in (x * (x - y), y * (y - x), 2 * x * y))


def nonparallel_frames(u, v, w):
    dirs = (u, v, w)
    frames = []
    for i, direction in enumerate(dirs):
        a = dirs[(i + 1) % 3]
        b = dirs[(i + 2) % 3]
        scale = Fraction(2 * dot(a, b), delta(direction, a) * delta(direction, b))
        frames.append(coefficient(direction, scale))
    return frames


def parallel_frames(u, w, scale_u):
    length_u = dot(u, u)
    length_w = dot(w, w)
    rho = Fraction(2, length_u)
    scale_w = Fraction(2, length_w)
    other = rho - scale_u
    return [
        coefficient(u, scale_u),
        coefficient(u, other),
        coefficient(w, scale_w),
    ]


def frame_sum(frames):
    return tuple(sum(frame[i] for frame in frames) for i in range(3))


def rank_one_nonzero(frame):
    a, b, c = frame
    if a == 0 and b == 0 and c == 0:
        return False
    det = a * b + c * (a + b) / 2
    return det == 0


def accepts(frames, form):
    x, y, z = form
    if (x - y) % 2 or (x - z) % 2 == 0:
        return False
    for frame in frames:
        value = x * frame[0] + y * frame[1] + z * frame[2]
        if value.denominator != 1 or int(value) % 2:
            return False
    return True


def character(frames):
    den = 2
    for frame in frames[:2]:
        for coordinate in frame:
            den = math.lcm(den, coordinate.denominator)

    def pack(frame, theta):
        row = [int(den * coordinate) for coordinate in frame]
        target = int((-den * theta) % den)
        return row, target

    for family, theta_of in (
        ("AB", lambda frame: (frame[0] + frame[1]) / 2),
        ("PQ", lambda frame: frame[2] / 2),
    ):
        c1, t1 = pack(frames[0], theta_of(frames[0]))
        c2, t2 = pack(frames[1], theta_of(frames[1]))
        solution = solve_two(c1, t1, c2, t2, den)
        if solution is None:
            continue
        p, s, t = solution
        if family == "AB":
            form = (1 + 2 * p, 1 + 2 * s, 2 * t)
        else:
            form = (2 * p, 2 * s, 1 + 2 * t)
        if accepts(frames, form):
            return family, form
    return None


def evaluate(form, vector):
    return form[0] * vector[0] + form[1] * vector[1] + form[2] * vector[2]


def detection_counts(form, frames):
    A = (1, 0, 0)
    B = (0, 1, 0)
    P = (0, 0, 1)
    Q = (1, 1, -1)
    calls = (A, B, P, Q, frames[0], frames[1], frames[2])
    targets = (
        (A[0] + P[0], A[1] + P[1], A[2] + P[2]),
        (A[0] + Q[0], A[1] + Q[1], A[2] + Q[2]),
        (B[0] + P[0], B[1] + P[1], B[2] + P[2]),
        (B[0] + Q[0], B[1] + Q[1], B[2] + Q[2]),
    )
    detected_calls = sum(int(evaluate(form, label)) % 2 for label in calls)
    detected_targets = sum(int(evaluate(form, label)) % 2 for label in targets)
    return detected_calls, detected_targets


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def polynomial_zero(diff, label):
    leftover = {key: value for key, value in diff.items() if value}
    require(not leftover, label + " has " + str(len(leftover)) + " nonzero monomials")


def scale_identity():
    def mul(left, right):
        out = Counter()
        for left_key, left_value in left.items():
            for right_key, right_value in right.items():
                key = tuple(a + b for a, b in zip(left_key, right_key))
                out[key] = out.get(key, 0) + left_value * right_value
                if out[key] == 0:
                    del out[key]
        return out

    def add(*parts):
        out = Counter()
        for part in parts:
            for key, value in part.items():
                out[key] = out.get(key, 0) + value
                if out[key] == 0:
                    del out[key]
        return out

    def constant(value):
        return Counter({(0, 0, 0, 0, 0, 0): value})

    def variable(index):
        exponents = [0] * 6
        exponents[index] = 1
        return Counter({tuple(exponents): 1})

    u1, u2, v1, v2, w1, w2 = (variable(i) for i in range(6))

    def dot_poly(a1, a2, b1, b2):
        return add(mul(a1, b1), mul(a2, b2))

    def delta_poly(a1, a2, b1, b2):
        return add(mul(a1, b2), {key: -value for key, value in mul(a2, b1).items()})

    duv = delta_poly(u1, u2, v1, v2)
    dvw = delta_poly(v1, v2, w1, w2)
    duw = delta_poly(u1, u2, w1, w2)
    vw = dot_poly(v1, v2, w1, w2)
    wu = dot_poly(w1, w2, u1, u2)
    uv = dot_poly(u1, u2, v1, v2)

    def cleared(quad_u, quad_v, quad_w, diagonal):
        numerator = add(
            mul(constant(2), mul(vw, mul(quad_u, dvw))),
            {key: -value for key, value in mul(constant(2), mul(wu, mul(quad_v, duw))).items()},
            mul(constant(2), mul(uv, mul(quad_w, duv))),
        )
        if diagonal:
            two_d = mul(constant(2), mul(duv, mul(duw, dvw)))
            numerator = add(numerator, {key: -value for key, value in two_d.items()})
        return numerator

    polynomial_zero(cleared(mul(u1, u1), mul(v1, v1), mul(w1, w1), True), "entry 00")
    polynomial_zero(cleared(mul(u2, u2), mul(v2, v2), mul(w2, w2), True), "entry 11")
    polynomial_zero(cleared(mul(u1, u2), mul(v1, v2), mul(w1, w2), False), "entry 01")

    # (u·v)δ(u,w) - (u·w)δ(u,v) - |u|^2 δ(v,w) = 0
    identity = add(
        mul(uv, duw),
        {key: -value for key, value in mul(wu, duv).items()},
        {key: -value for key, value in mul(add(mul(u1, u1), mul(u2, u2)), dvw).items()},
    )
    polynomial_zero(identity, "bracket identity")


def discriminant_lemma():
    checked = 0
    for alpha in (1, 3, 5, 7):
        for beta in (1, 3, 5, 7):
            if (alpha + beta) % 4:
                continue
            for gamma in (1, 3, 5, 7):
                residue = (alpha * beta - gamma * gamma) % 8
                require(residue in (2, 6), "discriminant residue " + str(residue))
                checked += 1
    require(checked == 32, "discriminant residue count " + str(checked))


def certify(frames, label):
    require(frame_sum(frames) == (2, 2, 0), label + " does not sum to 2I")
    for frame in frames:
        require(rank_one_nonzero(frame), label + " has a summand that is not nonzero rank one")
    found = character(frames)
    require(found is not None, label + " has no AB or PQ character")
    family, form = found
    calls, targets = detection_counts(form, frames)
    require(calls == 2 and targets == 4, label + " detects " + str(calls) + " calls and " + str(targets) + " targets")
    return family, form


def fixtures():
    certify(nonparallel_frames((1, 0), (2, 1), (1, 1)), "mixed parities")
    certify(nonparallel_frames((1, 0), (1, 2), (3, 2)), "three horizontal")
    certify(nonparallel_frames((-5, -4), (-5, -3), (-3, -5)), "negative valuation sample")
    certify(nonparallel_frames((0, 1), (1, 1), (-3, 1)), "vertical unit")
    certify(nonparallel_frames((1, 2), (3, 4), (5, 2)), "horizontal off axis")
    quarter = parallel_frames((1, -1), (1, 1), Fraction(1, 4))
    certify(quarter, "quarter split")
    require(accepts(quarter, (1, 1, 2)), "quarter split rejects a+b+2c")
    certify(parallel_frames((1, 0), (0, 1), Fraction(1, 3)), "orthogonal horizontal")
    certify(parallel_frames((2, 1), (-1, 2), Fraction(1, 5)), "orthogonal vertical")
    certify(parallel_frames((3, 1), (-1, 3), Fraction(1, 10)), "orthogonal diagonal")

    broken = list(nonparallel_frames((1, 0), (2, 1), (1, 1)))
    broken[2] = (broken[2][0] + 1, broken[2][1], broken[2][2])
    require(frame_sum(broken) != (2, 2, 0), "tampered triple still sums to 2I")
    identity = ((1, 0, 0), (0, 1, 0), (1, 1, 0))
    require(frame_sum(identity) == (2, 2, 0), "A+B+I setup")
    require(not rank_one_nonzero(identity[2]), "I was treated as rank one")
    require(not accepts(quarter, (2, 2, 2)), "even-even-even form was accepted")


def main():
    scale_identity()
    discriminant_lemma()
    fixtures()
    print("PASS three-signed-old-once character checks")


if __name__ == "__main__":
    main()
