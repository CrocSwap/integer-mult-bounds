#!/usr/bin/env python3
"""Check exact polynomial and resultant identities for prime-power inputs."""

from fractions import Fraction as F
from pathlib import Path
import argparse
import json
from math import gcd


def require(condition):
    if not condition:
        raise ValueError("Exact identity check failed")


def trim(a):
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def subtract(a, b):
    c = [F(0)] * max(len(a), len(b))
    for j, x in enumerate(a):
        c[j] += x
    for j, x in enumerate(b):
        c[j] -= x
    return trim(c)


def multiply(a, b):
    c = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    return trim(c)


def divide(a, b):
    a = trim(list(a))
    c = [F(0)] * max(1, len(a) - len(b) + 1)
    while a != [0] and len(a) >= len(b):
        k, x = len(a) - len(b), a[-1] / b[-1]
        c[k] += x
        for j, y in enumerate(b):
            a[k + j] -= x * y
        trim(a)
    return trim(c), a


class Field:
    def __init__(self, r):
        p = next(j for j in range(2, r + 1) if r % j == 0)
        remainder = r
        while remainder % p == 0:
            remainder //= p
        require(r >= 3 and remainder == 1)
        step = r // p
        self.q, self.n, self.prime = r, (p - 1) * step, p
        self.modulus = [F(0)] * (self.n + 1)
        for j in range(p):
            self.modulus[j * step] = F(1)
        self.zero = (F(0),) * self.n
        self.one = (F(1),) + (F(0),) * (self.n - 1)

    def reduce(self, a):
        a = divide(a, self.modulus)[1]
        return tuple(a + [F(0)] * (self.n - len(a)))

    def root(self, j):
        return self.reduce([F(0)] * (j % self.q) + [F(1)])

    def add(self, a, b):
        return tuple(x + y for x, y in zip(a, b))

    def sub(self, a, b):
        return tuple(x - y for x, y in zip(a, b))

    def scale(self, a, x):
        return tuple(y * x for y in a)

    def mul(self, a, b):
        return self.reduce(multiply(a, b))

    def inv(self, a):
        require(a != self.zero)
        r0, r1, s0, s1 = self.modulus, trim(list(a)), [F(0)], [F(1)]
        while r1 != [0]:
            c, r = divide(r0, r1)
            r0, r1 = r1, r
            s0, s1 = s1, subtract(s0, multiply(c, s1))
        require(len(r0) == 1 and r0[0] != 0)
        return self.reduce([x / r0[0] for x in s0])

    def embed(self, a, power):
        out = self.zero
        for j, x in enumerate(a):
            out = self.add(out, self.scale(self.root(power * j), x))
        return out

    def conjugate(self, a):
        return self.embed(a, -1)


def poly_product(k, a, b):
    out = [k.zero] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = k.add(out[i + j], k.mul(x, y))
    return out


def evaluate(k, a, z):
    out = k.zero
    for x in reversed(a):
        out = k.add(k.mul(out, z), x)
    return out


def sylvester(k, a, b):
    n = len(a) - 1
    require(len(b) == n + 1)
    out = [[k.zero for _ in range(2 * n)] for _ in range(2 * n)]
    for offset, polynomial in ((0, a), (n, b)):
        for j in range(n):
            for i, x in enumerate(polynomial):
                out[i + j][j + offset] = x
    return out


def eliminate(k, matrix, boundary=None):
    a = [list(row) for row in matrix]
    b = list(boundary) if boundary is not None else None
    determinant = k.one
    for col in range(len(a)):
        pivot = next((j for j in range(col, len(a)) if a[j][col] != k.zero), None)
        if pivot is None:
            return k.zero, None
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            if b is not None:
                b[col], b[pivot] = b[pivot], b[col]
            determinant = k.scale(determinant, -1)
        value = a[col][col]
        determinant = k.mul(determinant, value)
        reciprocal = k.inv(value)
        for j in range(col, len(a)):
            a[col][j] = k.mul(a[col][j], reciprocal)
        if b is not None:
            b[col] = k.mul(b[col], reciprocal)
        for row in range(len(a)):
            if row == col:
                continue
            value = a[row][col]
            for j in range(col, len(a)):
                a[row][j] = k.sub(a[row][j], k.mul(value, a[col][j]))
            if b is not None:
                b[row] = k.sub(b[row], k.mul(value, b[col]))
    return determinant, b


def case(r, power):
    k, n = Field(r), r - 1
    require(gcd(r, power) == 1)
    tail = [k.zero] * r
    tail[-1] = k.one
    for j in range(n - 1, -1, -1):
        tail[j] = k.mul(tail[j + 1], k.sub(k.one, k.root(power * (j + 1))))
    require(tail[0] == k.scale(k.one, r))
    kernel = [k.one]
    for j in range(1, r):
        kernel.append(k.mul(kernel[-1], k.inv(k.sub(k.one, k.root(power * j)))))
    require(tail == [k.scale(x, r) for x in kernel])
    for j in range(r):
        require(all(x.denominator == 1 for x in tail[j]))
        require(sum(tail[j]) % k.prime == (1 if j == n else 0))
    star = [k.conjugate(x) for x in reversed(tail)]
    require([k.conjugate(x) for x in reversed(star)] == tail)
    for j in range(r):
        require(sum(star[j]) % k.prime == (1 if j == 0 else 0))
    matrix = sylvester(k, tail, star)
    boundary = [k.one] + [k.zero] * (2 * n - 1)
    resultant, solution = eliminate(k, matrix, boundary)
    require(resultant != k.zero)
    require(all(x.denominator == 1 for x in resultant))
    residue = (-1) ** n % k.prime
    require(sum(resultant) % k.prime == residue)
    a, b = solution[:n], solution[n:]
    af, bs = poly_product(k, a, tail), poly_product(k, b, star)
    require([k.add(x, y) for x, y in zip(af, bs)] == boundary)
    norm = k.one
    for embedding in range(1, r):
        if gcd(embedding, r) == 1:
            norm = k.mul(norm, k.embed(resultant, embedding))
    require(all(x == 0 for x in norm[1:]) and norm[0].denominator == 1 and norm[0] != 0)
    for j in range(r):
        value, reverse = evaluate(k, tail, k.root(j)), evaluate(k, star, k.root(j))
        require(k.mul(value, k.conjugate(value)) == k.mul(reverse, k.conjugate(reverse)))
    unit = [k.scale(k.one, -1)] + [k.zero] * (n - 1) + [k.one]
    unit_star = [k.conjugate(x) for x in reversed(unit)]
    require(eliminate(k, sylvester(k, unit, unit_star))[0] == k.zero)
    bad_star = list(reversed(tail))
    require(any(k.mul(evaluate(k, tail, k.root(j)), k.conjugate(evaluate(k, tail, k.root(j)))) !=
               k.mul(evaluate(k, bad_star, k.root(j)), k.conjugate(evaluate(k, bad_star, k.root(j))))
               for j in range(r)))
    return {"radix": r, "prime": k.prime, "field_degree": k.n,
            "polynomial_degree": n, "primitive_power": power,
            "resultant": [str(x) for x in resultant], "resultant_norm": str(norm[0]),
            "bezout_identity": True, "mod_ideal_resultant": residue,
            "unit_root_negative_control": "singular",
            "missing_conjugation_negative_control": "rejected",
            "circle_bound_base": 2 ** r - 1,
            "circle_bound_exponent": n * k.n - 1,
            "circle_bound_denominator": 2 * r * n}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = [case(r, power) for r, power in
             ((3, 1), (4, 1), (5, 2), (7, 1), (8, 1), (9, 1), (11, 1), (11, 4))]
    result = {"status": "PASS", "cases": cases,
              "scope": "Exact finite identities. The written proof supplies the uniform theorem."}
    payload = json.dumps(result, indent=2) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.write_text(payload)
