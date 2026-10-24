#!/usr/bin/env python3
"""Exact finite component of the four-guard negative-association proof.

Krzysztof Wojt, with substantial OpenAI Codex assistance. Apache-2.0.
Intersection spectra: Nick Petalas, PR4227/4261/4275/4599.
No predecessor executable is imported.
"""

import json
from collections import defaultdict
from fractions import Fraction
from itertools import product
from math import comb, prod


SPECTRA = (
    {1: 1},
    {3: 1},
    {9: 1, 7: -2, 5: 1},
    {27: 1, 21: -6, 19: 6, 17: -6, 15: 16, 13: -18, 11: 9, 9: -2},
    {81: 1, 63: -12, 57: 24, 55: -8, 51: -24, 49: 18, 47: -48,
     45: 118, 43: -68, 41: 85, 39: -180, 37: 228, 35: -336, 33: 399,
     31: -444, 29: 502, 27: -548, 25: 523, 23: -332, 21: 144, 19: -48, 17: 6},
)

# Coefficient of p_j in the expectation of each increasing event.
EVENTS = {
    "x": (0, 1), "AND2": (0, 0, 1), "OR2": (0, 2, -1),
    "AND3": (0, 0, 0, 1), "xAND(yORz)": (0, 0, 2, -1),
    "MAJ3": (0, 0, 3, -2), "xOR(yANDz)": (0, 1, 1, -1),
    "OR3": (0, 3, -3, 1),
}
CASES = tuple((name, "x") for name in EVENTS) + (
    ("AND2", "AND2"), ("AND2", "OR2"), ("OR2", "OR2"),
)
# B, c, b, C, N: largest base and coefficient, next base, remaining mass, cutoff.
TAILS = (
    (28672, 128, 20480, 143872, 21),
    (21504, 128, 19456, 419520, 81),
    (28672, 256, 21504, 680640, 28),
    (16128, 96, 14592, 2820224, 103),
    (21504, 256, 19456, 3626656, 96),
    (21504, 384, 19456, 6850144, 98),
    (28672, 128, 21504, 3367488, 36),
    (28672, 384, 21504, 4395776, 33),
    (16128, 128, 14592, 2919872, 101),
    (21504, 256, 19456, 3726336, 96),
    (28672, 512, 21504, 5020608, 32),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(*terms):
    """Add (integer multiplier, {positive base: integer coefficient}) pairs."""
    result = defaultdict(int)
    for multiplier, polynomial in terms:
        for base, coefficient in polynomial.items():
            result[base] += multiplier * coefficient
    return {base: value for base, value in result.items() if value}


def multiply(left, right):
    """Pointwise multiply sequences represented as finite power sums."""
    result = defaultdict(int)
    for b, a in left.items():
        for d, c in right.items():
            result[b * d] += a * c
    return {base: value for base, value in result.items() if value}


def evaluate(polynomial, n):
    return sum(coefficient * base**n for base, coefficient in polynomial.items())


def numerator(k):
    """A_k with p_k=A_k/Q, Q=16^n product_(j=0)^3 (2^(n+1)-2^j)."""
    result = multiply(SPECTRA[k], {2**(4 - k): 1})
    for j in range(k, 4):
        result = multiply(result, {2: 2, 1: -(2**j)})
    return result


def gap_polynomial(f, g):
    numerators = tuple(numerator(k) for k in range(5))
    left = add(*[(a, numerators[i]) for i, a in enumerate(f)])
    right = add(*[(a, numerators[i]) for i, a in enumerate(g)])
    joint = add(*[(a * b, numerators[i + j])
                  for i, a in enumerate(f) for j, b in enumerate(g)])
    return add((1, multiply(left, right)), (-1, multiply(numerators[0], joint)))


def moments(m):
    require(type(m) is int and m >= 4, "dimension must be an integer at least four")
    n, x = m - 1, 2**m
    return tuple(Fraction(evaluate(SPECTRA[k], n),
                          2**(k * n) * prod(x - 2**j for j in range(k)))
                 for k in range(5))


def gap_value(f, g, p):
    return (sum(a * p[i] for i, a in enumerate(f)) *
            sum(b * p[j] for j, b in enumerate(g)) -
            sum(a * b * p[i + j] for i, a in enumerate(f) for j, b in enumerate(g)))


def tail_parameters(polynomial):
    require(len(polynomial) >= 2, "nontrivial tail required")
    bases = sorted(polynomial, reverse=True)
    require(all(type(b) is int and b > 0 for b in bases), "positive integer bases required")
    return (bases[0], polynomial[bases[0]], bases[1],
            sum(abs(polynomial[b]) for b in bases[1:]))


def verify_tail(polynomial, certificate):
    require(len(certificate) == 5 and all(type(v) is int for v in certificate),
            "five exact integer tail parameters required")
    require(tail_parameters(polynomial) == certificate[:4], "tail parameters differ")
    B, c, b, C, N = certificate
    require(B > b > 0 and c > 0 and C > 0 and N >= 3, "invalid strict tail domain")
    require(c * B**N > C * b**N, "tail dominance fails")


def monotone_tables(size):
    """Enumerate Boolean truth tables; bit x is the value at subset x."""
    return [table for table in range(1, (1 << (1 << size)) - 1)
            if all(not (table >> x & 1) or (table >> (x | (1 << i)) & 1)
                   for x in range(1 << size) for i in range(size))]


def expectation_coefficients(table, size):
    """Subset Mobius inversion, then group coefficients by degree."""
    coefficients = [table >> x & 1 for x in range(1 << size)]
    for i in range(size):
        for x in range(1 << size):
            if x >> i & 1:
                coefficients[x] -= coefficients[x ^ (1 << i)]
    result = [0] * (size + 1)
    for x, coefficient in enumerate(coefficients):
        result[x.bit_count()] += coefficient
    while result and not result[-1]:
        result.pop()
    return tuple(result)


def event_classification():
    expected = (
        {EVENTS["x"]: 1},
        {EVENTS["x"]: 2, EVENTS["AND2"]: 1, EVENTS["OR2"]: 1},
        {EVENTS["x"]: 3, EVENTS["AND2"]: 3, EVENTS["OR2"]: 3,
         EVENTS["AND3"]: 1, EVENTS["xAND(yORz)"]: 3, EVENTS["MAJ3"]: 1,
         EVENTS["xOR(yANDz)"]: 3, EVENTS["OR3"]: 1},
    )
    tables = {s: monotone_tables(s) for s in (1, 2, 3)}
    for size in (1, 2, 3):
        histogram = defaultdict(int)
        for table in tables[size]:
            histogram[expectation_coefficients(table, size)] += 1
        require(dict(histogram) == expected[size - 1], "monotone classification differs")
    known = {tuple(sorted(gap_polynomial(EVENTS[a], EVENTS[b]).items()))
             for a, b in CASES}
    seen, total = set(), 0
    for a, b in ((1, 1), (1, 2), (1, 3), (2, 2)):
        for f, g in product(tables[a], tables[b]):
            polynomial = gap_polynomial(expectation_coefficients(f, a),
                                        expectation_coefficients(g, b))
            seen.add(tuple(sorted(polynomial.items())))
            total += 1
    require(seen == known and len(known) == 11, "incomplete covariance list")
    return tables, total


def atom_probabilities(p, size):
    """Probability of each specified binary word from intersection moments."""
    return tuple(sum((-1)**j * comb(size - x.bit_count(), j) * p[x.bit_count() + j]
                     for j in range(size - x.bit_count() + 1))
                 for x in range(1 << size))


def literal_gap(f, a, g, b, atoms):
    """Truth-table evaluation without multilinear coefficients."""
    ef = eg = joint = Fraction(0)
    for x, mass in enumerate(atoms):
        fv = f >> (x & ((1 << a) - 1)) & 1
        gv = g >> ((x >> a) & ((1 << b) - 1)) & 1
        ef += fv * mass
        eg += gv * mass
        joint += fv * gv * mass
    return ef * eg - joint


def rejection_controls():
    p = gap_polynomial(EVENTS["AND3"], EVENTS["x"])
    tests = [
        lambda: moments(3), lambda: moments(True),
        lambda: verify_tail(add((-1, p)), TAILS[3]),
        lambda: verify_tail(p, (*TAILS[3][:4], 3)),
        lambda: verify_tail(p, (*TAILS[3][:3], TAILS[3][3] - 1, TAILS[3][4])),
        lambda: verify_tail(p, (*TAILS[3][:4], True)),
    ]
    for operation in tests:
        try:
            operation()
        except ValueError:
            continue
        raise ValueError("invalid proof input was accepted")
    bad_atoms = [Fraction(0)] * 16
    bad_atoms[0] = bad_atoms[15] = Fraction(1, 2)
    require(literal_gap(2, 1, 2, 1, bad_atoms) == -Fraction(1, 4),
            "positive-covariance control was not detected")
    wrong = Fraction(3**3, 2**3 * 16)
    require(wrong != Fraction(9, 40), "finite-GL denominator control is ineffective")
    return len(tests) + 2


def main():
    tables, labelled_cases = event_classification()
    require(moments(4) == (1, Fraction(9, 40), Fraction(1, 80), Fraction(1, 1680), 0),
            "complete GL4 moment fixture differs")
    atoms4 = atom_probabilities(moments(4), 4)
    require(tuple(20160 * q for q in atoms4) ==
            (3480, 3816, 3816, 228, 3816, 228, 228, 12,
             3816, 228, 228, 12, 228, 12, 12, 0), "GL4 atom fixture differs")
    rows, prefix_checks = [], 0
    Q = numerator(0)
    for (left, right), certificate in zip(CASES, TAILS, strict=True):
        f, g = EVENTS[left], EVENTS[right]
        polynomial = gap_polynomial(f, g)
        verify_tail(polynomial, certificate)
        N = certificate[4]
        for n in range(3, N):
            direct = gap_value(f, g, moments(n + 1))
            expanded = Fraction(evaluate(polynomial, n), evaluate(Q, n)**2)
            require(direct == expanded and direct > 0, "finite prefix sign/identity failed")
            prefix_checks += 1
        for n in (N, N + 1, 2 * N):
            require(Fraction(evaluate(polynomial, n), evaluate(Q, n)**2) ==
                    gap_value(f, g, moments(n + 1)) > 0, "tail probe failed")
        rows.append({"events": [left, right], "terms": len(polynomial),
                     "B_c_b_C_N": certificate})
    truth_checks = 0
    for m in range(4, max(row[4] for row in TAILS) + 2):
        p = moments(m)
        atoms = atom_probabilities(p, 4)
        require(sum(atoms) == 1 and min(atoms) >= 0, "invalid four-bit distribution")
        for a, b in ((1, 1), (1, 2), (1, 3), (2, 2)):
            for f, g in product(tables[a], tables[b]):
                literal = literal_gap(f, a, g, b, atoms)
                algebraic = gap_value(expectation_coefficients(f, a),
                                      expectation_coefficients(g, b), p)
                require(literal == algebraic and literal > 0, "truth-table covariance failed")
                truth_checks += 1
    controls = rejection_controls()
    print("PASS_CORANKONE_FOUR_NEGATIVE_ASSOCIATION")
    print(json.dumps({"claim": "strict negative association for every integer m >= 4",
                      "proof": "exact finite prefixes plus strict monotone power-sum tails",
                      "nonconstant_monotone_functions": [len(tables[s]) for s in (1, 2, 3)],
                      "labelled_cases": labelled_cases, "distinct_gap_types": len(rows),
                      "finite_prefix_comparisons": prefix_checks,
                      "truth_table_comparisons": truth_checks,
                      "tail_probe_comparisons": 3 * len(rows),
                      "rejection_controls": controls, "tails": rows}, sort_keys=True))


if __name__ == "__main__":
    main()
