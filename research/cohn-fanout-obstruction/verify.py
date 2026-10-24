#!/usr/bin/env python3
"""Exact identities for polynomial dirty fanout; Cohn's theorem is cited."""

import hashlib
import itertools
import json
from pathlib import Path


MAX_EXPONENT = 16
MAX_TERMS = 289
MAX_WORD = 8
PRIMES = (2, 3, 5, 7)
ZERO = ()
ONE = ((0, 0, 1),)
X = ((1, 0, 1),)
Y = ((0, 1, 1),)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def polynomial(terms):
    require(len(terms) <= MAX_TERMS, "polynomial input capacity")
    merged = {}
    for x, y, coefficient in terms:
        require(0 <= x <= MAX_EXPONENT and 0 <= y <= MAX_EXPONENT,
                "polynomial exponent capacity")
        require(type(coefficient) is int and coefficient.bit_length() <= 64,
                "integer coefficient capacity")
        merged[x, y] = merged.get((x, y), 0) + coefficient
    result = tuple((x, y, c) for (x, y), c in sorted(merged.items()) if c)
    require(len(result) <= MAX_TERMS, "polynomial output capacity")
    require(all(c.bit_length() <= 64 for _, _, c in result),
            "polynomial output coefficient capacity")
    return result


def add(a, b):
    require(len(a) + len(b) <= MAX_TERMS, "addition capacity")
    return polynomial(a + b)


def neg(a):
    return tuple((x, y, -c) for x, y, c in a)


def multiply(a, b):
    require(len(a) * len(b) <= MAX_TERMS, "multiplication capacity")
    return polynomial(tuple((x + u, y + v, c * d)
                            for x, y, c in a for u, v, d in b))


def evaluate(a, x, y, prime):
    require(prime in PRIMES and 0 <= x < prime and 0 <= y < prime,
            "field evaluation domain")
    return sum(c * pow(x, u, prime) * pow(y, v, prime)
               for u, v, c in a) % prime


def identity():
    return tuple(tuple(ONE if i == j else ZERO for j in range(3))
                 for i in range(3))


def matrix_product(a, b):
    require(len(a) == len(b) == 3, "three-row matrix domain")
    rows = []
    for i in range(3):
        row = []
        for j in range(3):
            entry = ZERO
            for k in range(3):
                entry = add(entry, multiply(a[i][k], b[k][j]))
            row.append(entry)
        rows.append(tuple(row))
    return tuple(rows)


def gate(kind, row, coefficient):
    require(kind in ("P", "E") and row in (0, 1), "gate domain")
    result = [list(r) for r in identity()]
    result[row][2 if kind == "P" else 1 - row] = coefficient
    return tuple(tuple(r) for r in result)


def endpoint(word):
    require(len(word) <= MAX_WORD, "word capacity")
    result = identity()
    for kind, row, coefficient in word:
        result = matrix_product(gate(kind, row, coefficient), result)
    return result


def inverse_word(word):
    require(len(word) <= MAX_WORD, "inverse word capacity")
    return tuple((kind, row, neg(c)) for kind, row, c in reversed(word))


def fixture():
    xy = multiply(X, Y)
    x2, y2 = multiply(X, X), multiply(Y, Y)
    demand = (add(ONE, xy), x2)
    cohn_transpose = ((demand[0], neg(y2), ZERO),
                      (x2, add(ONE, neg(xy)), ZERO),
                      (ZERO, ZERO, ONE))
    cohn_inverse = ((add(ONE, neg(xy)), y2, ZERO),
                    (neg(x2), demand[0], ZERO),
                    (ZERO, ZERO, ONE))
    target = ((ONE, ZERO, demand[0]), (ZERO, ONE, demand[1]),
              (ZERO, ZERO, ONE))
    return demand, cohn_transpose, cohn_inverse, target


def candidates(demand):
    x, y = demand
    direct = (("P", 0, x), ("P", 1, y))
    into_zero = (("E", 1, neg(ONE)), ("P", 0, y),
                 ("E", 1, ONE), ("P", 0, add(x, neg(y))))
    into_one = (("E", 0, neg(ONE)), ("P", 1, x),
                ("E", 0, ONE), ("P", 1, add(y, neg(x))))
    return direct, into_zero, into_one


def counts(word):
    return tuple(sum(kind == k and row == r for kind, row, _ in word)
                 for k, r in (("P", 0), ("P", 1), ("E", 0), ("E", 1)))


def scalar_execution(word, values, x, y, prime):
    result = list(values)
    for kind, row, coefficient in word:
        source = 2 if kind == "P" else 1 - row
        result[row] = (result[row] + evaluate(coefficient, x, y, prime)
                       * result[source]) % prime
    return tuple(result)


def identities_and_controls():
    demand, cohn, cohn_inverse, target = fixture()
    require(matrix_product(cohn, cohn_inverse) == identity(), "Cohn inverse")
    require(matrix_product(cohn_inverse, cohn) == identity(), "left inverse")
    bezout = add(multiply(demand[0], cohn[1][1]),
                 multiply(demand[1], multiply(Y, Y)))
    require(bezout == ONE, "unimodular demand identity")
    controls = 0
    words = candidates(demand)
    expected_counts = ((1, 1, 0, 0), (2, 0, 0, 2), (0, 2, 2, 0))
    for word, expected in zip(words, expected_counts):
        require(counts(word) == expected, "candidate counts")
        require(endpoint(word) == target, "complete affine endpoint")
        require(matrix_product(endpoint(inverse_word(word)), target) == identity(),
                "inverse restores source and arbitrary dirt")
        for removed in range(len(word)):
            require(endpoint(word[:removed] + word[removed + 1:]) != target,
                    "single deletion must fail")
            controls += 1
    # An arbitrary SL2 row gate defeats the obstruction. It is not free.
    relaxed = matrix_product(cohn, matrix_product(gate("P", 0, ONE), cohn_inverse))
    require(relaxed == target, "changed-alphabet control")
    require(endpoint(tuple(reversed(words[1]))) != target, "order control")
    naive = (("E", 1, neg(demand[1])), ("P", 0, demand[0]),
             ("E", 1, demand[1]))
    require(endpoint(naive) != target, "false polynomial division control")
    controls += 3
    for t in (ZERO, ONE, X, Y, add(X, Y), multiply(X, Y)):
        completion = matrix_product(cohn, gate("E", 0, t))
        require(tuple(completion[i][0] for i in range(2)) == demand,
                "completion column")
        require(matrix_product(cohn_inverse, completion) == gate("E", 0, t),
                "completion coset identity")
    return words, controls


def specializations(words):
    demand, _, _, _ = fixture()
    scalar_checks, one_insertions = 0, 0
    for prime in PRIMES:
        for x, y in itertools.product(range(prime), repeat=2):
            a, b = (evaluate(c, x, y, prime) for c in demand)
            require(a != 0 or b != 0, "specialized demand is unimodular")
            # Every field specialization DOES have a one-insertion word.
            alpha = 0 if a else 1
            beta = (a - alpha * b) % prime
            r = b * pow(beta, -1, prime) % prime
            scalar_word = (("E", 0, polynomial(((0, 0, -alpha),))),
                           ("E", 1, polynomial(((0, 0, -r),))),
                           ("P", 0, polynomial(((0, 0, beta),))),
                           ("E", 1, polynomial(((0, 0, r),))),
                           ("E", 0, polynomial(((0, 0, alpha),))))
            for basis in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                expected = ((basis[0] + a * basis[2]) % prime,
                            (basis[1] + b * basis[2]) % prime, basis[2])
                require(scalar_execution(scalar_word, basis, x, y, prime) == expected,
                        "field specialization one-insertion witness")
            one_insertions += 1
            for values in itertools.product(range(prime), repeat=3):
                expected = ((values[0] + a * values[2]) % prime,
                            (values[1] + b * values[2]) % prime, values[2])
                for word in words:
                    actual = scalar_execution(word, values, x, y, prime)
                    require(actual == expected, "arbitrary scalar input")
                    require(scalar_execution(inverse_word(word), actual, x, y, prime)
                            == values, "arbitrary scalar inverse")
                    scalar_checks += 1
    return scalar_checks, one_insertions


def price_checks(words):
    vectors = tuple(counts(word) for word in words)
    comparisons = 0
    for prices in itertools.product(range(1, 6), repeat=4):
        measured = tuple(sum(a * b for a, b in zip(v, prices)) for v in vectors)
        mu0, mu1, c0, c1 = prices
        formula = (mu0 + mu1, 2 * mu0 + 2 * c1, 2 * mu1 + 2 * c0)
        require(measured == formula, "complete candidate invoice")
        comparisons += 1
    for winner, prices in enumerate(((1, 1, 1, 1), (1, 10, 1, 1), (10, 1, 1, 1))):
        costs = tuple(sum(a * b for a, b in zip(v, prices)) for v in vectors)
        require(all(costs[winner] < costs[j] for j in range(3) if j != winner),
                "each Pareto vector has a strict positive-price witness")
    return comparisons


def boundary_controls():
    rejected = 0
    for terms in (((17, 0, 1),), ((0, 0, True),), ((0, 0, 1 << 65),)):
        try:
            polynomial(terms)
        except ValueError:
            rejected += 1
    try:
        evaluate(ONE, 0, 0, 4)
    except ValueError:
        rejected += 1
    require(rejected == 4, "invalid domains must reject")
    return rejected


def main():
    words, controls = identities_and_controls()
    scalar_checks, one_insertions = specializations(words)
    prices = price_checks(words)
    controls += boundary_controls()
    package = Path(__file__).resolve().parent
    files = sorted(p for p in package.iterdir() if p.suffix in (".py", ".md", ".json"))
    require(len(files) <= 12, "receipt file capacity")
    hashes = {}
    for path in files:
        with path.open("rb") as stream:
            data = stream.read(131073)
        require(len(data) <= 131072, "receipt file byte capacity")
        hashes[path.name] = hashlib.sha256(data).hexdigest()
    receipt = {"claim_type": "scoped proof using cited Cohn theorem",
               "scalar_forward_inverse_pairs": scalar_checks,
               "field_specializations_with_one_insertion": one_insertions,
               "price_vectors": prices, "controls": controls,
               "cohn_non_elementarity_machine_verified": False, "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))
    print(f"PASS_COHN_FANOUT scalar_pairs={scalar_checks} "
          f"specializations={one_insertions} prices={prices} controls={controls} no_new_kappa")


if __name__ == "__main__":
    main()
