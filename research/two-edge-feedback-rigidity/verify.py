#!/usr/bin/env python3
"""Exact corroboration of the reduced two-edge rigidity theorem.

New theorem and verifier produced by Nick Petalas. Apache-2.0.
No predecessor scientific program is imported or executed.
"""

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform


IDENTITY = (1, 0, 0, 1)
ZERO = (0, 0, 0, 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b, modulus):
    return tuple((a[i] + b[i]) % modulus for i in range(4))


def neg(a, modulus):
    return tuple(-a[i] % modulus for i in range(4))


def mul(a, b, modulus):
    return (
        (a[0] * b[0] + a[1] * b[2]) % modulus,
        (a[0] * b[1] + a[1] * b[3]) % modulus,
        (a[2] * b[0] + a[3] * b[2]) % modulus,
        (a[2] * b[1] + a[3] * b[3]) % modulus,
    )


def inverse(a, modulus):
    determinant = (a[0] * a[3] - a[1] * a[2]) % modulus
    need(math.gcd(determinant, modulus) == 1, "matrix is not a unit")
    scale = pow(determinant, -1, modulus)
    result = tuple(scale * x % modulus for x in (a[3], -a[1], -a[2], a[0]))
    need(mul(a, result, modulus) == mul(result, a, modulus) == IDENTITY,
         "matrix inverse failed")
    return result


def validate(q, c, d, modulus):
    need(type(modulus) is int and modulus in (2, 3, 4), "unsupported modulus")
    for value in (q, c, d):
        need(type(value) is tuple and len(value) == 4,
             "matrix must have four entries")
        need(all(type(x) is int and 0 <= x < modulus for x in value),
             "matrix entries must be canonical integers")
    qi = inverse(q, modulus)
    inverse(d, modulus)
    need(mul(c, c, modulus) == IDENTITY, "C is not an involution")
    need(mul(q, d, modulus) == mul(d, q, modulus), "Q and D do not commute")
    return qi


def row(q, c, d, b, f, g, modulus):
    """Block-row evaluation of B + Q^-1 G Q^-1 (K + F L)."""
    qi = inverse(q, modulus)
    h = mul(mul(qi, c, modulus), d, modulus)
    k = (ZERO, neg(mul(q, d, modulus), modulus), mul(c, d, modulus), ZERO)
    late = (h, d, neg(h, modulus), ZERO)
    left = mul(mul(qi, g, modulus), qi, modulus)
    base = (ZERO, ZERO, b, ZERO)
    return tuple(add(base[i], mul(left, add(k[i], mul(f, late[i], modulus),
                                          modulus), modulus), modulus)
                 for i in range(4))


def action(matrix, vector, modulus):
    return ((matrix[0] * vector[0] + matrix[1] * vector[1]) % modulus,
            (matrix[2] * vector[0] + matrix[3] * vector[1]) % modulus)


def literal(q, c, d, b, f, g, inputs, modulus):
    """Evaluate the two feedback applications on values, without block rows."""
    qi = inverse(q, modulus)
    x, y, z, _ = inputs
    dx, dy, dz = (action(d, v, modulus) for v in (x, y, z))
    h0 = action(qi, action(c, dx, modulus), modulus)
    h2 = action(qi, action(c, dz, modulus), modulus)
    late = tuple((h0[i] + dy[i] - h2[i]) % modulus for i in range(2))
    first, second = action(c, dz, modulus), action(q, dy, modulus)
    feedback = action(f, late, modulus)
    argument = tuple((first[i] - second[i] + feedback[i]) % modulus
                     for i in range(2))
    response = action(qi, argument, modulus)
    feed = action(qi, action(g, response, modulus), modulus)
    base = action(b, z, modulus)
    return tuple((base[i] + feed[i]) % modulus for i in range(2))


def matrices(modulus):
    need(modulus in (2, 3, 4), "matrix enumeration is bounded by modulus four")
    return tuple(itertools.product(range(modulus), repeat=4))


def binary_fixtures():
    values = matrices(2)
    units = tuple(a for a in values if (a[0] * a[3] - a[1] * a[2]) % 2)
    involutions = tuple(c for c in units if mul(c, c, 2) == IDENTITY)
    return tuple((2, q, c, d) for q in units for c in involutions for d in units
                 if mul(q, d, 2) == mul(d, q, 2))


def census(fixture):
    modulus, q, c, d = fixture
    qi = validate(q, c, d, modulus)
    b = (1, 1, 0, 1)
    target = (mul(d, qi, modulus), ZERO, b, ZERO)
    expected = (q, mul(c, q, modulus))
    accepted = []
    tested = 0
    for f in matrices(modulus):
        for g in matrices(modulus):
            tested += 1
            output = row(q, c, d, b, f, g, modulus)
            if output == target:
                accepted.append((f, g))
            # Check the stronger two-constraint characterization separately.
            aggregate = add(output[0], output[2], modulus)
            reduced = output[1] == ZERO and aggregate == add(target[0], b, modulus)
            need(reduced == (output == target), "aggregate characterization failed")
    need(accepted == [expected], "finite solution set is not the unique pair")
    return {"modulus": modulus, "Q": q, "C": c, "D": d,
            "pairs_tested": tested, "solutions": accepted}


def literal_checks(fixture):
    modulus, q, c, d = fixture
    qi = validate(q, c, d, modulus)
    b = (1, 1, 0, 1)
    f, g = q, mul(c, q, modulus)
    checked = 0
    for raw in itertools.product(range(modulus), repeat=8):
        inputs = tuple((raw[i], raw[i + 1]) for i in range(0, 8, 2))
        first = action(mul(d, qi, modulus), inputs[0], modulus)
        third = action(b, inputs[2], modulus)
        expected = tuple((first[i] + third[i]) % modulus for i in range(2))
        need(literal(q, c, d, b, f, g, inputs, modulus) == expected,
             "literal arbitrary-input endpoint failed")
        checked += 1
    return checked


def controls():
    modulus = 3
    q, c, d = (0, 1, 2, 0), (1, 0, 0, 2), IDENTITY
    qi = validate(q, c, d, modulus)
    b = IDENTITY
    target = (qi, ZERO, b, ZERO)
    need(mul(q, c, modulus) != mul(c, q, modulus), "noncommuting control collapsed")
    wrong_order = row(q, c, d, b, q, mul(q, c, modulus), modulus)
    need(wrong_order != target, "wrong multiplication order was accepted")
    old = row(q, c, d, b, IDENTITY, mul(mul(c, q, modulus), q, modulus), modulus)
    need(old[0] == target[0] and old != target, "first-column-only control failed")
    missing = row(q, c, d, b, q, ZERO, modulus)
    need(missing[1] == ZERO and missing != target, "zero-y-only control failed")
    rejected = 0
    invalid = ((ZERO, c, d, 3), (q, c, ZERO, 3),
               (q, ZERO, d, 3), (q, c, c, 3),
               (q, c, d, True), ((False, 1, 2, 0), c, d, 3))
    for args in invalid:
        try:
            validate(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid fixture was accepted")
    return {"wrong_order_rejected": True, "first_column_alone_insufficient": True,
            "zero_y_alone_insufficient": True, "invalid_fixtures_rejected": rejected}


def source_hashes():
    here = Path(__file__).resolve().parent
    names = ("verify.py", "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    return {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in names}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a new hash-bound receipt outside the package")
    args = parser.parse_args()
    if args.receipt is not None:
        need(args.receipt.is_absolute(), "receipt path must be absolute")
        need(not args.receipt.is_relative_to(Path(__file__).resolve().parent),
             "receipt must be outside the package")
    fixtures = binary_fixtures() + (
        (3, (0, 1, 2, 0), (1, 0, 0, 2), (0, 1, 2, 0)),
        (3, (1, 1, 0, 1), (0, 1, 1, 0), IDENTITY),
        (4, (1, 1, 0, 1), (0, 1, 1, 0), (1, 2, 0, 1)),
    )
    results = [census(fixture) for fixture in fixtures]
    literal_cases = sum(literal_checks(fixture) for fixture in fixtures[-3:])
    result = {"status": "PASS_TWO_EDGE_FEEDBACK_RIGIDITY",
              "claim_type": "scoped written proof with exact finite corroboration",
              "python": platform.python_version(), "fixtures": len(fixtures),
              "pairs_tested": sum(item["pairs_tested"] for item in results),
              "unique_solutions": len(results), "literal_inputs_checked": literal_cases,
              "controls": controls(), "censuses": results, "files_sha256": source_hashes()}
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.receipt is not None:
        with args.receipt.open("x", encoding="utf-8") as handle:
            written = handle.write(payload)
            need(written == len(payload), "partial receipt write")
    print(payload, end="")


if __name__ == "__main__":
    main()
