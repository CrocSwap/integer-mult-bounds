"""Numerical Fraction checks using negative prefixes and literal full suffixes.

This file imports no executable code from the symbolic verifier or predecessors.
"""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
N = 36
SELECTED = (0, 1, 2, 4, 6, 8, 10, 12, 14, 18, 19, 20, 22, 24, 26, 28, 30, 32, 34, 36)
SOURCE_HASH = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"


def check(condition, message):
    if not condition:
        raise ValueError(message)


def eye():
    return [[F(i == j) for j in range(N)] for i in range(N)]


def inner(first, second):
    return sum(x * y for x, y in zip(first, second, strict=True) if x and y)


def axpy(first, second, value):
    return [x + value * y for x, y in zip(first, second, strict=True)]


def sign(profile, stages):
    return -1 if sum((profile >> (stage - 1)) & 1 for stage in stages) % 2 else 1


def shear(rows, inverse_columns, dest, source, value):
    rows[dest] = axpy(rows[dest], rows[source], value)
    inverse_columns[source] = axpy(inverse_columns[source], inverse_columns[dest], -value)


def diagonal(rows, inverse_columns, dest, value):
    rows[dest] = [value * x for x in rows[dest]]
    inverse_columns[dest] = [x / value for x in inverse_columns[dest]]


def paid(rows, inverse_columns, factors, dest, source, value):
    image = inverse_columns[dest].copy()
    covector = [2 * value * x for x in rows[source]]
    check(inner(image, covector) == 0, "literal factor nilpotence")
    factors.append((image, covector))
    shear(rows, inverse_columns, dest, source, -value)


def ordinary(event, profile, rows, inverse_columns, factors):
    _, operation, dest, *args = event
    if operation == "ADD":
        shear(rows, inverse_columns, dest, args[0], F(args[1]))
    elif operation == "QUERY":
        check(args[1] == -1, "literal query exponent")
        paid(rows, inverse_columns, factors, dest, args[0], 1)
    elif operation == "SWAP":
        source = args[0]
        rows[dest], rows[source] = rows[source], rows[dest]
        inverse_columns[dest], inverse_columns[source] = inverse_columns[source], inverse_columns[dest]
    elif operation == "SCALE":
        diagonal(rows, inverse_columns, dest, F(args[0]))
    elif operation == "IDLE_ONE":
        diagonal(rows, inverse_columns, dest, sign(profile, args[0]))
    else:
        check(operation == "LAMBDA", "literal ordinary operation")


def negative_factors(caller, profile):
    rows, inverse_columns, factors = eye(), eye(), []
    for event in caller["events"]:
        if event[0] == "B":
            continue
        if event[0] == "J":
            _, stage, (a, b, c, d), _ = event
            paid(rows, inverse_columns, factors, b, a, 1)
            paid(rows, inverse_columns, factors, c, d, -1)
            for role in (a, b, c, d):
                diagonal(rows, inverse_columns, role, sign(profile, [stage]))
        else:
            check(event[0] == "A", "literal event family")
            ordinary(event, profile, rows, inverse_columns, factors)
    check(len(factors) == 38, "literal factor inventory")
    for row in range(N):
        powers = caller["types"]["A"]["diagonal"][row][2:]
        stages = [j + 1 for j, power in enumerate(powers) if power]
        expected = [-sign(profile, stages) * x for x in eye()[row]]
        check(rows[row] == expected, "literal negative endpoint")
    return factors


def transport(factors):
    result = []
    for index in SELECTED:
        image, covector = factors[index]
        for later in range(index + 1, 38):
            u, v = factors[later]
            image = axpy(image, u, inner(v, image))
            covector = axpy(covector, v, -inner(covector, u))
        check(inner(image, covector) == 0, "literal transported nilpotence")
        result.append((image, covector))
    return result


def evaluate(factors, column):
    for image, covector in reversed(factors):
        column = axpy(column, image, inner(covector, column))
    return column


def compare(actual, reference, diagonal_signs):
    entries = 0
    for (image, covector), (old_image, old_covector) in zip(actual, reference, strict=True):
        for row in range(N):
            for col in range(N):
                check(image[row] * covector[col] == diagonal_signs[row] * diagonal_signs[col]
                      * old_image[row] * old_covector[col], "literal conjugacy entry")
                entries += 1
    for index, column in enumerate(eye()):
        expected = evaluate(reference, [diagonal_signs[index] * x for x in column])
        expected = [s * x for s, x in zip(diagonal_signs, expected, strict=True)]
        check(evaluate(actual, column) == expected, "selected product conjugacy")
    return entries


def main():
    raw = (ROOT / "inputs/CALLER.json").read_bytes()
    check(len(raw) <= 2**20 and sha256(raw).hexdigest() == SOURCE_HASH, "literal source pin")
    caller = json.loads(raw)
    check(len(caller["events"]) == 4783, "literal event cap")
    reference = transport(negative_factors(caller, 0))
    profiles = [1 << j for j in range(17)] + [3, 2**17 - 1, 0b10101010101010101, 0b11111111100000000]
    check(len(profiles) == len(set(profiles)) == 21, "profile inventory")
    entries, omissions = 0, 0
    for profile in profiles:
        actual = transport(negative_factors(caller, profile))
        chain = [sign(profile, range(1, min(max(j - 1, 0), 8) + 1)) for j in range(18)]
        entries += compare(actual, reference, chain + chain)
        check(any(evaluate(actual[1:], column) != evaluate(actual, column) for column in eye()),
              "omitted selected factor was accepted")
        omissions += 1
    print(json.dumps({"profiles": profiles, "entry_comparisons": entries,
                      "omitted_factor_controls": omissions, "source_sha256": SOURCE_HASH,
                      "program_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}, sort_keys=True))
    print(f"PASS_INDEPENDENT_REAL_BODY_GAUGE profiles={len(profiles)} entries={entries} omissions={omissions}")


if __name__ == "__main__":
    main()
