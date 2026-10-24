#!/usr/bin/env python3
"""Exact finite checks for the all-field pair law. Produced by Nick Petalas."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field(p, modulus):
    """Tables for the fixed fields, with polynomial-basis extension arithmetic."""
    degree = len(modulus) - 1
    q = p**degree
    require(q in (2, 3, 4, 5, 7, 8, 9), "unsupported field size")
    digits = [tuple((i // p**j) % p for j in range(degree)) for i in range(q)]
    addition, multiplication = [], []
    for a, b in product(digits, repeat=2):
        addition.append(sum((a[i] + b[i]) % p * p**i for i in range(degree)))
        coefficients = [0] * (2 * degree - 1)
        for i, j in product(range(degree), repeat=2):
            coefficients[i + j] = (coefficients[i + j] + a[i] * b[j]) % p
        for k in range(2 * degree - 2, degree - 1, -1):
            for j in range(degree):
                coefficients[k - degree + j] -= coefficients[k] * modulus[j]
        multiplication.append(sum(coefficients[i] % p * p**i for i in range(degree)))
    add = tuple(tuple(addition[a * q : (a + 1) * q]) for a in range(q))
    mul = tuple(tuple(multiplication[a * q : (a + 1) * q]) for a in range(q))
    neg = tuple(next(b for b in range(q) if add[a][b] == 0) for a in range(q))
    sub = tuple(tuple(add[a][neg[b]] for b in range(q)) for a in range(q))
    for a in range(1, q):
        require(sum(mul[a][b] == 1 for b in range(q)) == 1, "missing inverse")
    for a, b, c in product(range(q), repeat=3):
        require(mul[a][add[b][c]] == add[mul[a][b]][mul[a][c]], "distributivity")
    return q, sub, mul


def invariants(matrix, mul):
    a, b, c, d = matrix
    zeros = int(b == 0) + int(c == 0)
    singular = int(mul[a][d] == mul[b][c])
    return zeros, singular


def transition(source, target, q, sub, mul):
    a, b, c, d = (sub[x][y] for x, y in zip(source, target, strict=True))
    if a == b == c == d == 0:
        return 2 * q * q - 1
    return q - 1 if mul[a][d] == mul[b][c] else 0


def parameters(q):
    return (q * q - q + 1) ** 2, q**3 - q + 1, q**3 - q * q + 1


def numerator(q, n):
    alpha, beta, gamma = parameters(q)
    value = Fraction((q - 1) ** 2, q * q) * (alpha**n - 2 * beta**n + gamma**n)
    require(value.denominator == 1 and value >= 0, "nonintegral count")
    return value.numerator


def check_identities(q, states, samples, sub, mul):
    alpha, beta, gamma = parameters(q)
    constant = (q - 1) ** 2 * (q * q - 3 * q + 4)
    target_values = [invariants(b, mul) for b in states]
    for source in samples:
        total, zero_sum, terminal = 0, 0, 0
        for target, (zeros, singular) in zip(states, target_values, strict=True):
            weight = transition(source, target, q, sub, mul)
            total += weight
            zero_sum += weight * zeros
            terminal += weight * singular * (q - 1)
        zeros, singular = invariants(source, mul)
        require(total == alpha, "T1 identity")
        require(zero_sum == 2 * (q - 1) ** 3 + beta * zeros, "Tz identity")
        require(
            terminal == constant - (q - 1) ** 2 * zeros + gamma * (q - 1) * singular,
            "Th identity",
        )
    return len(samples) * len(states)


def check_transfer(q, states, sub, mul):
    """Independent full-state evolution, without the invariant quotient."""
    rows = [tuple(transition(a, b, q, sub, mul) for b in states) for a in states]
    terminal = [(q - 1) * invariants(b, mul)[1] for b in states]
    start = states.index((1, 0, 0, 1))
    for n in range(9):
        require(terminal[start] == numerator(q, n), "closed form versus transfer")
        if n < 8:
            terminal = [
                sum(w * v for w, v in zip(row, terminal, strict=True)) for row in rows
            ]
    return [numerator(q, n) for n in range(1, 5)]


def factor_count_controls(q, sub, mul):
    """Enumerate literal outer products, independently of determinant weights."""
    counts = {}
    for u, v, x, y in product(range(q), repeat=4):
        matrix = (mul[u][x], mul[u][y], mul[v][x], mul[v][y])
        counts[matrix] = counts.get(matrix, 0) + 1
    zero = (0, 0, 0, 0)
    for matrix in product(range(q), repeat=4):
        require(
            counts.get(matrix, 0) == transition(matrix, zero, q, sub, mul),
            "literal factor multiplicity",
        )
    require(counts[zero] != 2 * q * q, "zero multiplicity mutant survived")
    return q**4


def check_headers(q, sub, mul):
    """Literal complete GL2 headers and both conjugated one-pivot requests."""
    invertible, passing = 0, 0
    for a, b, c, d in product(range(q), repeat=4):
        determinant = sub[mul[a][d]][mul[b][c]]
        if determinant == 0:
            continue
        invertible += 1
        inverse_det = next(x for x in range(1, q) if mul[determinant][x] == 1)
        inverse_00 = mul[d][inverse_det]
        inverse_10 = mul[sub[0][c]][inverse_det]
        # G diag(1,0) G^-1 and G diag(0,1) G^-1, at their only pivot.
        passing += int(mul[a][inverse_00] != 0 and mul[b][inverse_10] != 0)
    require(invertible == (q * q - 1) * (q * q - q), "complete GL2 domain")
    require(passing == numerator(q, 1), "literal full-guard header count")
    return {"total": invertible, "passing": passing}


def check_polynomials():
    """A degree-at-most-10 identity is fixed by 11 distinct integer evaluations."""
    for q in range(2, 13):
        alpha, beta, gamma = parameters(q)
        constant = (q - 1) ** 2 * (q * q - 3 * q + 4)
        c1 = (q - 1) ** 3 * (q - 2)
        c2 = (
            constant * alpha - (q - 1) ** 2 * (2 * (q - 1) ** 3 + 2 * beta) + gamma * c1
        )
        require((q - 1) ** 2 * (alpha - 2 * beta + gamma) == q * q * c1, "initial c1")
        require(
            (q - 1) ** 2 * (alpha**2 - 2 * beta**2 + gamma**2) == q * q * c2,
            "initial c2",
        )
    return 11


def controls():
    require(numerator(2, 1) == 0 and numerator(2, 2) == 2, "binary boundary")
    require(numerator(3, 1) == 8 and numerator(3, 2) == 672, "ternary boundary")
    require(numerator(5, 1) == 192 and numerator(5, 2) == 112256, "quinary fixture")
    alpha, beta, gamma = parameters(5)
    require(
        Fraction(16, 25) * (alpha - 2 * beta + gamma + 1) != 192,
        "wrong last eigenvalue mutant survived",
    )
    require(
        Fraction(16, 25) * (alpha - beta + gamma) != 192,
        "missing negative coefficient mutant survived",
    )
    joint = Fraction(numerator(5, 1), (25 - 1) * (25 - 5))
    marginal = Fraction(4 * 21, (25 - 1) * 5)
    require(joint == Fraction(2, 5) and joint != marginal**2, "independence control")
    _, _, mul = field(2, (1, 1, 1))
    require(mul[2][2] == 3 and (2 * 2) % 4 == 0, "F4 must not be Z/4Z")
    return 7


def main():
    specifications = (
        (2, (0, 1)),
        (3, (0, 1)),
        (2, (1, 1, 1)),
        (5, (0, 1)),
        (7, (0, 1)),
        (2, (1, 1, 0, 1)),
        (3, (1, 0, 1)),
    )
    domains, transitions, factors = [], 0, 0
    for p, modulus in specifications:
        q, sub, mul = field(p, modulus)
        states = [
            (a, b, c, d)
            for a, b, c, d in product(range(q), repeat=4)
            if a != 0 and d != 0
        ]
        samples = (
            states
            if q <= 5
            else [(1, 0, 0, 1), (1, 1, 0, 1)] + [(1, 1, t, 1) for t in range(1, q)]
        )
        transitions += check_identities(q, states, samples, sub, mul)
        factors += factor_count_controls(q, sub, mul)
        row = {
            "q": q,
            "states": len(states),
            "sources": len(samples),
            "GL2_headers": check_headers(q, sub, mul),
        }
        if q <= 5:
            row["numerators_n1_to_n4"] = check_transfer(q, states, sub, mul)
        domains.append(row)
    root = Path(__file__).resolve().parent
    names = (
        "README.md",
        "PROOF.md",
        "TASK.json",
        "SOURCES.json",
        "VERIFY.json",
        "verify.py",
    )
    receipt = {
        "domains": domains,
        "identity_transition_pairs": transitions,
        "literal_factor_tuples": factors,
        "polynomial_evaluations": check_polynomials(),
        "controls": controls(),
        "sha256": {
            name: sha256((root / name).read_bytes()).hexdigest() for name in names
        },
    }
    print("PASS_CORANKONE_ALL_FIELD_LAW " + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
