#!/usr/bin/env python3
"""Exact finite evidence for the all-field one-way full-guard formula."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field(q):
    """Tables for seven explicitly bounded prime and extension fields."""
    specs = {2: (2, (0, 1)), 3: (3, (0, 1)), 4: (2, (1, 1, 1)),
             5: (5, (0, 1)), 7: (7, (0, 1)), 8: (2, (1, 1, 0, 1)),
             9: (3, (1, 0, 1))}
    require(q in specs, "unsupported field order")
    p, modulus = specs[q]
    degree = len(modulus) - 1
    digits = tuple(tuple((a // p**i) % p for i in range(degree))
                   for a in range(q))
    add, mul = [], []
    for a, b in product(digits, repeat=2):
        add.append(sum(((a[i] + b[i]) % p) * p**i for i in range(degree)))
        coeff = [0] * (2 * degree - 1)
        for i, j in product(range(degree), repeat=2):
            coeff[i + j] = (coeff[i + j] + a[i] * b[j]) % p
        for k in range(2 * degree - 2, degree - 1, -1):
            for j in range(degree):
                coeff[k - degree + j] -= coeff[k] * modulus[j]
        mul.append(sum((coeff[i] % p) * p**i for i in range(degree)))
    neg = tuple(next(b for b in range(q) if add[a * q + b] == 0)
                for a in range(q))
    require(all(any(mul[a * q + b] == 1 for b in range(q))
                for a in range(1, q)), "nonunit in field table")
    return tuple(add), tuple(mul), neg


def subtract(a, b, q, add, neg):
    return add[a * q + neg[b]]


def determinant(matrix, q, add, mul, neg):
    a, b, c, d = matrix
    return subtract(mul[a * q + d], mul[b * q + c], q, add, neg)


def closed(q, n):
    require(2 <= q <= 128 and 0 <= n <= 128, "formula replay bounds")
    alpha = (q * q - q + 1)**2
    beta, gamma = q**3 - q + 1, q**3 - q * q + 1
    numerator = (q - 1) * ((q - 1) * alpha**n
                          - (q - 2) * beta**n - gamma**n)
    require(numerator % (q * q) == 0, "nonintegral numerator")
    return numerator // (q * q)


def transfer_cases(q):
    """Use the cited raw partial-Gram walk, with no invariant quotient."""
    add, mul, neg = field(q)
    states = tuple(a for a in product(range(q), repeat=4)
                   if a[0] != 1 and a[3] != 1)
    weights = []
    for a in product(range(q), repeat=4):
        weights.append(2 * q * q - 1 if not any(a) else
                       q - 1 if determinant(a, q, add, mul, neg) == 0 else 0)
    transitions, terminal = [], []
    for a in states:
        row = []
        for b in states:
            delta = tuple(subtract(x, y, q, add, neg)
                          for x, y in zip(a, b, strict=True))
            index = sum(x * q**(3 - i) for i, x in enumerate(delta))
            row.append(weights[index])
        transitions.append(tuple(row))
        delta = tuple(subtract(x, y, q, add, neg)
                      for x, y in zip((1, 1, 0, 1), a, strict=True))
        index = sum(x * q**(3 - i) for i, x in enumerate(delta))
        terminal.append(weights[index])
    counts = [int(a == (0, 0, 0, 0)) for a in states]
    for n in range(9):
        actual = sum(a * b for a, b in zip(counts, terminal, strict=True))
        require(actual == closed(q, n), f"raw transfer mismatch q={q}, n={n}")
        if n < 8:
            counts = [sum(w * c for w, c in zip(row, counts, strict=True))
                      for row in transitions]
    return 9, len(states)**2


def complete_gl2(q):
    """Literal first guards after conjugating U=e1(e1+e2)^T, V=e2e2^T."""
    add, mul, neg = field(q)
    total = good = 0
    for a, b, c, d in product(range(q), repeat=4):
        det = determinant((a, b, c, d), q, add, mul, neg)
        if det == 0:
            continue
        total += 1
        # Clear the common nonzero determinant in each conjugated guard.
        u11 = mul[a * q + subtract(d, c, q, add, neg)]
        v11 = mul[b * q + neg[c]]
        good += (subtract(det, u11, q, add, neg) != 0
                 and subtract(det, v11, q, add, neg) != 0)
    require(total == (q * q - 1) * (q * q - q), "GL2 size mismatch")
    require(good == closed(q, 1), "literal GL2 header mismatch")
    return {"q": q, "headers": total, "passing": good,
            "fraction": str(Fraction(good, total))}


def coefficient_cases():
    """Check the new closed expression against its three-coordinate update."""
    cases = 0
    for q in range(2, 65):
        r = q - 1
        alpha, beta, gamma = (q * q - q + 1)**2, q**3 - q + 1, q**3 - q*q + 1
        a, b, c = 0, 0, 1
        for n in range(65):
            require(a + b == closed(q, n), "coefficient solution mismatch")
            require(a + 2*b == Fraction(r*r, q*q)
                    * (alpha**n - 2*beta**n + gamma**n), "orthogonal boundary")
            cases += 1
            a, b, c = (alpha*a + 2*r**3*b + r*r*(q*q-3*q+4)*c,
                       beta*b-r*r*c, gamma*c)
    return cases


def controls():
    q, n = 3, 1
    alpha, beta, gamma = 49, 25, 19
    require(closed(q, n) != Fraction(2, 9)*(2*alpha-2*beta-gamma),
            "beta coefficient mutation escaped")
    require(closed(q, n) != Fraction(2, 9)*(2*alpha-beta+gamma),
            "gamma sign mutation escaped")
    require(closed(q, n) != Fraction(4, 9)*(2*alpha-beta-gamma),
            "prefactor mutation escaped")
    require(closed(2, 1) == 1, "one-way binary boundary")
    require(Fraction(1, 6) != Fraction(1, 2)**2, "independence control")
    add, _, _ = field(4)
    require(add[1*4+1] == 0 and (1+1) % 4 != 0, "F4 confused with Z/4Z")
    for q, n in ((1, 1), (129, 1), (2, -1), (2, 129)):
        try:
            closed(q, n)
        except ValueError:
            continue
        raise ValueError("formula bound did not reject")
    return 10


def main():
    coefficient_count = coefficient_cases()
    transfer_count = transitions = 0
    for q in (2, 3, 4, 5):
        cases, pairs = transfer_cases(q)
        transfer_count += cases
        transitions += pairs
    headers = [complete_gl2(q) for q in (2, 3, 4, 5, 7, 8, 9)]
    require(Fraction(closed(3, 2), (27-1)*(27-3)*9) == Fraction(53, 351),
            "cited one-way ternary boundary")
    root = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
             "VERIFY.json", "verify.py")
    receipt = {"status": "PASS_ONEWAY_ALL_FIELD_CLOSED_FORM",
               "coefficient_cases": coefficient_count,
               "raw_transfer_cases": transfer_count,
               "source_target_pairs": transitions,
               "complete_gl2": headers, "controls": controls(),
               "sha256": {name: sha256((root/name).read_bytes()).hexdigest()
                          for name in names}}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
