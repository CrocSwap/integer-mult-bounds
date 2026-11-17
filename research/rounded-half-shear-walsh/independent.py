#!/usr/bin/env python3
"""Independent dense integer/Fraction interpreter; no primary imports."""

import hashlib
import itertools
import json
from fractions import Fraction
import struct


def check(condition, message):
    if not condition:
        raise ArithmeticError(message)


def matvec(matrix, vector):
    return tuple(sum(row[j] * vector[j] for j in range(4)) for row in matrix)


def rounded_ratio(n, denominator):
    # Select the closer of two consecutive integers.
    low = n // denominator
    left = n - denominator * low
    right = denominator - left
    if left < right:
        return low
    if left > right:
        return low + 1
    return low if low % 2 == 0 else low + 1


def matrices(target, source):
    a2 = ((1, 1, 0, 0), (1, -1, 0, 0),
          (0, 0, 1, 1), (0, 0, 1, -1))
    b2 = ((1, 0, 1, 0), (0, 1, 0, 1),
          (1, 0, -1, 0), (0, 1, 0, -1))
    s2 = tuple(tuple(2 * (i == j) + (i == target and j == source)
                     for j in range(4)) for i in range(4))
    return a2, s2, b2


def dense(x, gates):
    state = x
    ideal = x
    for gate in gates:
        state = tuple(rounded_ratio(v, 2) for v in matvec(gate, state))
        ideal = matvec(gate, ideal)
    return tuple(8 * state[j] - ideal[j] for j in range(4))


def fractional(x, gates, omit_middle_round=False):
    state = tuple(Fraction(v) for v in x)
    ideal = state
    for step, gate in enumerate(gates):
        state = tuple(v / 2 for v in matvec(gate, state))
        if not (step == 1 and omit_middle_round):
            state = tuple(Fraction(round(v)) for v in state)
        ideal = tuple(v / 2 for v in matvec(gate, ideal))
    result = tuple(8 * (state[j] - ideal[j]) for j in range(4))
    check(all(v.denominator == 1 for v in result), "eighth-unit error")
    return tuple(int(v) for v in result)


def run():
    digest = hashlib.sha256()
    count = 0
    rows = []
    oracle_checks = 0
    for target in range(4):
        for source in range(4):
            if target == source:
                continue
            gates = matrices(target, source)
            histogram = [0] * 10
            for x in itertools.product(range(16), repeat=4):
                error = dense(x, gates)
                maximum = max(map(abs, error))
                check(maximum <= 9, "dense upper bound")
                histogram[maximum] += 1
                digest.update(struct.pack("4b", *error))
                count += 1
            check(histogram[9] > 0, "dense sharpness")
            rows.append([target, source, histogram])
            for x in itertools.product((-3, -1, 0, 2), repeat=4):
                check(dense(x, gates) == fractional(x, gates),
                      "complete-vector Fraction oracle")
                oracle_checks += 1
    check(count == 12 * 16**4, "dense coverage")
    return {"status": "PASS_INDEPENDENT_HALF_SHEAR_WALSH", "cases": count,
            "rows": rows, "fraction_oracle_cases": oracle_checks,
            "error_stream_sha256": digest.hexdigest()}


def semantic_controls():
    gates = matrices(0, 1)
    x = (1, -1, 1, 1)
    check(fractional(x, gates) != fractional(x, gates, True),
          "omitting the internal rounding changes the program")
    x = (1, 4, 0, 1)
    correct = fractional(x, gates)
    identity2 = tuple(tuple(2 * (i == j) for j in range(4)) for i in range(4))
    omitted = fractional(x, (gates[0], identity2, gates[2]))
    check(correct != omitted, "omitting the shear changes the comparison")
    check(correct != fractional(x, tuple(reversed(gates))),
          "reversing the word changes the endpoint")
    check(rounded_ratio(-1, 2) == 0 and rounded_ratio(-3, 2) == -2,
          "signed tie control")
    return 4


def main():
    report = run()
    report["semantic_controls"] = semantic_controls()
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
